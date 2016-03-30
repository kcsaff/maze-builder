#  Following roughly http://www-cs-students.stanford.edu/~amitp/game-programming/polygon-map-generation/
import random
from pyhull.voronoi import VoronoiTess
from maze_builder.meshes.vertex_list import VertexList
from maze_builder.meshes.tiling import Tiling, Junction, Border, Region
from maze_builder.meshes.quadtree import StaticQuadTree
from maze_builder.meshes.geometry import BoundingBox
from PIL import Image, ImageDraw
import noise
import math

def _to_color(c):
    return min(255, int(256 * c))


class World(Tiling):
    def __init__(self, vertices, polygons, bbox=None):
        used_polygons = list()
        for polygon in polygons:
            using_polygon = True
            for index in polygon:
                vertex = vertices[index]
                if not using_polygon:
                    break
                for coord in vertex:
                    if coord < -10:
                        using_polygon = False
                        break
            if using_polygon:
                used_polygons.append(list(reversed(polygon)))

        super().__init__(
            vertices, used_polygons,
            junction_class=WorldJunction, border_class=WorldBorder, region_class=WorldRegion
        )
        print(self.regions)
        self.global_bbox = bbox or BoundingBox.around(vertices)
        self.ocean = set()

    @property
    def quadtree(self):
        if self._quadtree is None:
            self._quadtree = StaticQuadTree(self.regions, self.global_bbox)
        return self._quadtree

    def create_rockiness(self, noise):
        for junction in self.junctions:
            junction.rockiness = noise(junction.vertex)

    def create_water(self, noise, threshold=0):
        is_water = lambda region: noise(region.centroid()) < threshold
        seas = list()
        regions = set(self.regions)
        while regions:
            region = regions.pop()
            if is_water(region):
                region.is_fresh = True
                sea = {region}
                seas.append(sea)
                region.sea = sea
                potential_sea_regions = {region for region in region.neighbors() if region in regions}
                while potential_sea_regions:
                    potential_sea_region = potential_sea_regions.pop()
                    regions.remove(potential_sea_region)
                    if is_water(potential_sea_region):
                        sea.add(potential_sea_region)
                        potential_sea_region.is_fresh = True
                        potential_sea_region.sea = sea
                        potential_sea_regions.update(region for region in potential_sea_region.neighbors() if region in regions)
        sea_sizes = [sum(region.area() for region in sea) for sea in seas]
        ocean_size = max(sea_sizes)
        ocean_index = sea_sizes.index(ocean_size)
        self.ocean = seas[ocean_index]
        for region in self.ocean:
            region.is_ocean = True

    def set_coast_height(self, height=0):
        for region in self.ocean:
            for junction in region.junctions:
                junction.height = 0
        for border in self.borders.values():
            if border.is_coast:
                for junction in border.junctions:
                    junction.depth = 0

    def generate_heights(self):
        junctions = set(junction for junction in self.junctions if junction.height is not None)
        while junctions:
            junction = junctions.pop()
            for border in junction.borders:
                neighbor = border.other(junction)
                if not border.is_land:
                    candidate = junction.height
                else:
                    candidate = junction.height + neighbor.rockiness
                if neighbor.height is None or candidate < neighbor.height:
                    neighbor.height = candidate
                    junctions.add(neighbor)

    def generate_depths(self):
        junctions = set(junction for junction in self.junctions if junction.depth is not None)
        while junctions:
            junction = junctions.pop()
            for border in junction.borders:
                neighbor = border.other(junction)
                if border.is_water:
                    candidate = junction.depth + neighbor.rockiness
                    if neighbor.depth is None or candidate < neighbor.depth:
                        neighbor.depth = candidate
                        junctions.add(neighbor)

    def generate_rivers(self):
        for region in self.regions:
            if region.is_land:
                amount = region.area()
                junction = region.lowest_junction()
                junction.seepage += amount
                while junction.is_land:
                    border = junction.lowest_border()
                    junction = border.add_river(junction, amount)

    def generate_wetness(self):
        junctions = set()
        for junction in self.junctions:
            if junction.is_water or junction.has_fresh or junction.river > junction.seepage:
                junction.dryness = 0
                junctions.add(junction)

        while junctions:
            junction = junctions.pop()
            for border in junction.borders:
                if border.is_land:
                    neighbor = border.other(junction)
                    candidate = junction.dryness + border.length()
                    if neighbor.dryness is None or candidate < neighbor.dryness:
                        neighbor.dryness = candidate
                        junctions.add(neighbor)

        max_dryness = max(j.dryness for j in self.junctions if j.dryness is not None)
        for j in self.junctions:
            if j.dryness is None:
                j.dryness = max_dryness * 1.1

    def _color(self, region, max_height, max_depth, max_rockiness, max_dryness, multiplier=1.0, force_water=False):
        rel_rockiness = (region.rockiness() / max_rockiness)**(1/3)
        rel_height = region.height() / max_height
        rel_depth = (region.depth() / max_depth)**0.7
        rel_dryness = (region.dryness() / max_dryness)**0.5
        if not force_water and region.is_land:
            wet_color = (0.10 * rel_height, 0.50, 0.25 * rel_height)
            dry_color = (0.5 + 0.5 * rel_height, 0.25 + 0.75 * rel_height, 0.25 * rel_height)
            dirt_color = tuple(
                (wc + rel_dryness * (dc - wc))
                for wc, dc in zip(wet_color, dry_color)
            )
            rocky_color = tuple(0.25 + 0.75 * rel_height for _ in range(3))
            color = tuple(
                _to_color(multiplier * (dc + rel_rockiness * (rc - dc)))
                for rc, dc in zip(rocky_color, dirt_color)
            )
        else:
            color = (
                _to_color(0.2 * rel_rockiness * multiplier * (1-rel_depth)),
                _to_color(multiplier * (1-0.45*rel_depth) * rel_height**0.7),
                _to_color(multiplier * 0.75 * (1-0.65*rel_depth))
            )
        return color

    def save_image(self, filename='world.png'):
        x0 = self.global_bbox.p0[0]
        xd = int(self.global_bbox.p1[0] - x0)
        y0 = self.global_bbox.p0[1]
        yd = int(self.global_bbox.p1[1] - y0)

        image = Image.new('RGB', (xd, yd))
        draw = ImageDraw.Draw(image)

        max_height = max(region.height() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_depth = max(region.depth() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_rockiness = max(region.rockiness() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_dryness = max(region.dryness() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_river = max(border.river for border in self.borders.values())

        for i, region in enumerate(self.regions):
            poly = [
                (int(x - x0), int(y - y0)) for x, y in region
            ]
            draw.polygon(
                poly,
                fill=self._color(region, max_height, max_depth, max_rockiness, max_dryness),
                outline=self._color(region, max_height, max_depth, max_rockiness, max_dryness, multiplier=0.90)
            )

        for i, border in enumerate(self.borders.values()):
            rel_river = (border.river / max_river)**0.5
            width = int(6*rel_river)
            if width > 0:
                line = sum(
                    ((int(j.vertex[0] - x0), int(j.vertex[1] - y0)) for j in border.junctions),
                    ()
                )
                draw.line(
                    line,
                    fill=self._color(border, max_height, max_depth, max_rockiness, max_dryness, force_water=True),
                    width=width
                )

        image.save(filename)


class WorldJunction(Junction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height = None
        self.depth = None
        self.dryness = None
        self.rockiness = 0
        self.seepage = 0

    def distance(self, pt):
        return math.sqrt(sum((x-y)**2 for x, y in zip(pt, self.vertex)))

    def lowest_border(self):
        borders = list(self.borders)
        heights = [border.other(self).height for border in borders]
        lowest_index = heights.index(min(heights))
        return borders[lowest_index]

    @property
    def river(self):
        return sum(border.river for border in self.borders) / 2

    @property
    def is_coast(self):
        return any(region.is_water for region in self.regions) \
            and any(region.is_land for region in self.regions)

    @property
    def has_fresh(self):
        return any(region.is_fresh for region in self.regions)

    @property
    def is_land(self):
        return all(region.is_land for region in self.regions)

    @property
    def is_water(self):
        return all(region.is_water for region in self.regions)


class WorldBorder(Border):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.river = 0

    def add_river(self, source, amount):
        sink = self.other(source)
        self.river += amount
        return sink

    def rockiness(self):
        return sum(junction.rockiness for junction in self.junctions) / len(self.indices)

    def height(self):
        return sum(junction.height for junction in self.junctions if junction.height) / len(self.indices)

    def dryness(self):
        return sum(junction.dryness for junction in self.junctions if junction.dryness) / len(self.indices)

    def depth(self):
        return sum(junction.depth for junction in self.junctions if junction.depth) / len(self.indices)

    def length(self):
        junctions = tuple(self.junctions)
        return junctions[0].distance(junctions[1].vertex)

    @property
    def is_coast(self):
        return any(region.is_water for region in self.regions) \
            and any(region.is_land for region in self.regions)

    @property
    def is_water(self):
        return all(region.is_water for region in self.regions)

    @property
    def is_land(self):
        return all(region.is_land for region in self.regions)


class WorldRegion(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_land = True
        self._is_ocean = False
        self.sea = None

    @property
    def is_water(self):
        return not self.is_land

    @is_water.setter
    def is_water(self, is_water):
        self.is_land = not is_water

    @property
    def is_ocean(self):
        return self.is_water and self._is_ocean

    @is_ocean.setter
    def is_ocean(self, is_ocean):
        self.is_water = True
        self._is_ocean = True

    @property
    def is_fresh(self):
        return self.is_water and not self._is_ocean

    @is_fresh.setter
    def is_fresh(self, is_fresh):
        self.is_water = True
        self._is_ocean = False

    def lowest_junction(self):
        junctions = list(self.junctions)
        heights = [junction.height for junction in junctions]
        lowest_index = heights.index(min(heights))
        return junctions[lowest_index]

    def height(self, point=None):
        return self._property(point or self.centroid(), lambda junction: junction.height or 0)

    def depth(self, point=None):
        return self._property(point or self.centroid(), lambda junction: junction.depth or 0)

    def rockiness(self, point=None):
        return self._property(point or self.centroid(), lambda junction: junction.rockiness or 0)

    def dryness(self, point=None):
        return self._property(point or self.centroid(), lambda junction: junction.dryness if junction.dryness is not None else 100)

    def _property(self, point, fun):
        total_weight = 0
        total_property = 0
        for junction in self.junctions:
            distance = junction.distance(point)
            property = fun(junction)
            if distance < 0.01:
                return property
            weight = distance**-2
            total_weight += weight
            total_property += weight * property
        return total_property / total_weight


class WorldGenerator(object):
    def __init__(self, dims=(800, 800), seeds=12500):
        self.xdim, self.ydim = dims
        self.seeds = seeds

    def generate_world(self):
        pts = [
            (self.xdim * (-0.1 + 1.2 * random.random()),
             self.ydim * (-0.1 + 1.2 * random.random()))
            for _ in range(self.seeds)
        ]
        voronoi = VoronoiTess(pts)
        world = World(voronoi.vertices, voronoi.regions, BoundingBox((0, 0), (self.xdim, self.ydim)))
        xr = 100 * random.random()
        yr = 100 * random.random()
        xh = 100 * random.random()
        yh = 100 * random.random()
        world.create_water(lambda p: noise.pnoise2(xr + p[0] / 256, yr + p[1] / 256, 8) -
                                     0.15 * ((p[0]/self.xdim)**2 + (p[1]/self.ydim)**2),
                           -0.15)
        world.set_coast_height()
        world.create_rockiness(lambda p: math.exp(2.5 + 5 * noise.pnoise2(xh + p[0] / 128, yh + p[1] / 128, 8)))
        world.generate_heights()
        world.generate_depths()
        world.generate_rivers()
        world.generate_wetness()
        return world


if __name__ == '__main__':
    world = WorldGenerator((800, 800), 15000).generate_world()
    #world = WorldGenerator((200, 200), 1100).generate_world()
    world.save_image()
