#  Following roughly http://www-cs-students.stanford.edu/~amitp/game-programming/polygon-map-generation/
import random
from pyhull.voronoi import VoronoiTess
from maze_builder.meshes.tiling import Tiling, Junction, Border, Region
from maze_builder.meshes.quadtree import StaticQuadTree
from maze_builder.meshes.geometry import BoundingBox
from PIL import Image, ImageDraw
import noise
import math
import uuid
from collections import deque


inf = float('inf')


def _to_color(c):
    return min(255, int(256 * c))


class Destination(object):
    def __init__(self, region, world, name=None):
        self.region = region
        self.world = world
        self.distances = {self.region: 0}
        self.final = {self.region}
        self.followers = dict()
        self.name = name or str(uuid.uuid4())
        self.calculated = False

    def calculate(self):
        regions = deque()

        # Use previously calculated paths
        for destination in self.world.destinations:
            if destination.calculated and destination is not self and self.region in destination.distances:
                total = destination.distances[self.region]
                region = self.region
                while True:
                    follower = destination.followers.get(region)
                    if not follower:
                        break
                    other = follower.other(region)
                    self.followers[other] = follower
                    self.distances[other] = total - destination.distances[other]
                    self.final.add(other)
                    region = other

        for seed in self.final:
            regions.extend(self._seed(seed))

        while regions:
            preborder, source, region, distance = regions.popleft()
            distance += self.distances[source]
            if self.world.global_bbox.contains(region.centroid()) \
                    and (region not in self.distances or
                         distance < self.distances[region]):
                self.followers[region] = preborder
                self.distances[region] = distance
                regions.extend(self._seed(region))
        self.calculated = True

        return self

    def _seed(self, region, start=False):
        return (
            (border, region, border.other(region), border.walking_cost)
            for border in region.borders
            if border.is_land and len(border.regions) >=2 and \
               (border.other(region) not in self.final)
        )

    def mark(self, other, amount=1):
        best_distance = inf
        best = None
        for region, distance in self.distances.items():
            total_distance = distance + other.distances.get(region, inf)
            if total_distance < best_distance:
                best_distance = total_distance
                best = region

        if best is not None:
            self.mark_following(best, amount)
            other.mark_following(best, amount)

    def mark_following(self, region, amount=1):
        border = self.followers.get(region)
        while border:
            border.hiking_trail += amount
            region = border.other(region)
            border = self.followers.get(region)

class World(Tiling):
    def __init__(self, vertices, polygons, bbox=None):
        self.destinations = list()
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
        self.seas = list()
        self.coasts = list()

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
        self.seas = list()
        self.coasts = list()
        regions = set(self.regions)
        while regions:
            region = regions.pop()
            if is_water(region):
                region.is_fresh = True
                sea = {region}
                self.seas.append(sea)
                coast = set()
                self.coasts.append(coast)

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
                    else:
                        coast.add(potential_sea_region)

        sea_sizes = [sum(region.area() for region in sea) for sea in self.seas]
        ocean_size = max(sea_sizes)
        ocean_index = sea_sizes.index(ocean_size)
        self.ocean = self.seas[ocean_index]
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
                amount = region.area() * region.rainfall
                junction = region.lowest_junction()
                junction.seepage += amount
                while junction.is_land:
                    border = junction.lowest_border()
                    junction = border.add_river(junction, amount)

    def generate_wetness(self):
        junctions = set()
        for junction in self.junctions:
            if junction.is_water or junction.has_fresh:
                junction.dryness = 0
                junctions.add(junction)
            elif junction.river > 0:
                junction.dryness = 10 * junction.river**-0.5
                junctions.add(junction)

        while junctions:
            junction = junctions.pop()
            for border in junction.borders:
                if border.is_land:
                    neighbor = border.other(junction)
                    candidate = junction.dryness + border.length() * (1 + border.rockiness())
                    if neighbor.dryness is None or candidate < neighbor.dryness:
                        neighbor.dryness = candidate
                        junctions.add(neighbor)

        max_dryness = max(j.dryness for j in self.junctions if j.dryness is not None)
        for j in self.junctions:
            if j.dryness is None:
                j.dryness = max_dryness * 1.1

    def travel_cost(self, border, region=None, other=None):
        if len(border.regions) < 2:
            return inf
        elif region is None and other is None:
            region, other = tuple(border.regions)[:2]
        elif other is None:
            other = border.other(region)
        elif region is None:
            region = border.other(other)
        return 0.2 * border.river + abs(region.height() - other.height())

    def adjusted_travel_cost(self, border, region=None, other=None):
        if len(border.regions) < 2:
            return inf
        else:
            return self.travel_cost(border, region, other) / (1 + border.game_trail)

    def generate_game_trails(self):
        for region in self.regions:
            if region.is_land:
                amount = region.area()
                visited = set()
                while True:
                    visited.add(region)
                    borders1 = [(border, border.other(region))
                               for border in region.borders]

                    borders = [(border, other) for border, other in borders1
                               if other is not None and other not in visited and other.is_land]

                    if not borders:
                        break
                    border_heights = [self.travel_cost(border, region, other) for border, other in borders]
                    min_border_index = border_heights.index(min(border_heights))
                    border, region = borders[min_border_index]
                    border.game_trail += amount

    def generate_peakness(self):
        for region in self.regions:
            if region.is_land:
                amount = region.area()
                junction = region.highest_junction()
                border = junction.highest_border()
                while border:
                    junction = border.other(junction)
                    border = junction.highest_border()
                junction.peakness += amount

    def generate_walking_costs(self):
        for border in self.borders.values():
            border.game_cost = self.travel_cost(border)
        for border in self.borders.values():
            border.walking_cost = self.adjusted_travel_cost(border)

    def generate_destinations(self, sea_limit=5, peak_limit=5):
        coasts = [(len(coast), coast) for coast in self.coasts if len(coast) >= 2]
        coasts.sort(key=lambda el: el[0])
        coasts = [list(coast) for _, coast in coasts[:sea_limit]]
        for coast in coasts:
            region = random.choice(coast)
            destination = Destination(region, self, 'seaside')
            self.destinations.append(destination)

        print(len(self.destinations))

        peaknesses = [(j.peakness, j) for j in self.junctions if self.global_bbox.contains(j.vertex)]
        peaknesses.sort(key=lambda el: el[0])

        top_peaks = list(reversed(peaknesses[-peak_limit:]))
        for peakness, peak in top_peaks:
            if peakness > 0:
                destination = Destination(peak.highest_region(), self, 'peak')
                self.destinations.append(destination)

        print('precalculating destination distances')
        for destination in self.destinations:
            print('precalculating `{}`'.format(destination.name))
            destination.calculate()

    def generate_hiking_trails(self, trail_count=100):
        for _ in range(trail_count):
            d0, d1 = random.sample(self.destinations, 2)
            d0.mark(d1, 0.25 + random.random())

    def _color(self, region, max_height, max_depth, max_rockiness, max_dryness, multiplier=1.0, force_water=False):
        rel_rockiness = (region.rockiness() / max_rockiness)**(1/3)
        rel_height = region.height() / max_height
        rel_depth = (region.depth() / max_depth)**0.7
        rel_dryness = (region.dryness() / max_dryness)**0.5
        if not force_water and region.is_land:
            wet_color = (0.25 * rel_height, 0.25 + 0.75 * rel_height, 0.50 * rel_height)
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
                _to_color(multiplier * 0.75 * (1-0.65*rel_depth)),
            )
        return color + (255,)

    def save_image(self, filename='world.png'):
        x0 = self.global_bbox.p0[0]
        xd = int(self.global_bbox.p1[0] - x0)
        y0 = self.global_bbox.p0[1]
        yd = int(self.global_bbox.p1[1] - y0)

        image = Image.new('RGB', (xd, yd))
        draw = ImageDraw.Draw(image, 'RGBA')

        max_height = max(region.height() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_depth = max(region.depth() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_rockiness = max(region.rockiness() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_dryness = max(region.dryness() for region in self.regions if self.global_bbox.contains(region.centroid()))
        max_river = max(border.river for border in self.borders.values())
        max_game_trail = max(border.game_trail for border in self.borders.values())
        max_hiking_trail = max(border.hiking_trail for border in self.borders.values())

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
            width = int(8*rel_river)
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

        if max_game_trail > 0:
            for i, border in enumerate(self.borders.values()):
                rel_game_trail = (border.game_trail / max_game_trail)**0.5
                width = int(4*rel_game_trail)
                if width > 0:
                    line = sum(
                        ((int(r.centroid()[0] - x0), int(r.centroid()[1] - y0)) for r in border.regions),
                        ()
                    )
                    draw.line(
                        line,
                        fill=(0, 0, 0, 32),
                        width=width
                    )

        if max_hiking_trail > 0:
            for i, border in enumerate(self.borders.values()):
                rel_hiking_trail = (border.hiking_trail / max_hiking_trail)**0.5
                width = int(5*rel_hiking_trail)
                if width > 0:
                    line = sum(
                        ((int(r.centroid()[0] - x0), int(r.centroid()[1] - y0)) for r in border.regions),
                        ()
                    )
                    draw.line(
                        line,
                        fill=(0, 0, 0, 255),
                        width=width
                    )

        if self.destinations:
            for i, destination in enumerate(self.destinations):
                c = destination.region.centroid()
                b = 3
                bbox = (c[0]-b, c[1]-b, c[0]+b, c[1]+b)
                draw.ellipse(bbox, (192, 0, 0, 192), (64, 0, 0, 192))

        image.save(filename)


class WorldJunction(Junction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height = None
        self.depth = None
        self.dryness = None
        self.rockiness = 0
        self.seepage = 0
        self.peakness = 0

    def distance(self, pt):
        return math.sqrt(sum((x-y)**2 for x, y in zip(pt, self.vertex)))

    def lowest_border(self):
        borders = list(self.borders)
        heights = [border.other(self).height for border in borders]
        lowest_index = heights.index(min(heights))
        return borders[lowest_index]

    def highest_border(self):
        borders = list(self.borders)
        heights = [border.other(self).height for border in borders]
        highest_index = heights.index(max(heights))
        border = borders[highest_index]
        if border.other(self).height > self.height:
            return border
        else:
            return None

    def highest_region(self):
        regions = list(self.regions)
        heights = [region.height() for region in regions]
        highest_index = heights.index(max(heights))
        return regions[highest_index]

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
        self.game_trail = 0
        self.hiking_trail = 0
        self.walking_cost = None
        self.game_cost = None

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
        self.rainfall = 1

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

    def highest_junction(self):
        junctions = list(self.junctions)
        heights = [junction.height for junction in junctions]
        highest_index = heights.index(max(heights))
        return junctions[highest_index]

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
    def __init__(self, dims=(800, 800), seeds=12500, margin=0.07):
        self.xdim, self.ydim = dims
        self.seeds = seeds
        self.margin = margin

    def generate_world(self):
        pts = [
            (self.xdim * (-self.margin + (1+2*self.margin) * random.random()),
             self.ydim * (-self.margin + (1+2*self.margin) * random.random()))
            for _ in range(self.seeds)
        ]
        voronoi = VoronoiTess(pts)
        world = World(voronoi.vertices, voronoi.regions, BoundingBox((0, 0), (self.xdim, self.ydim)))
        xr = 100 * random.random()
        yr = 100 * random.random()
        xh = 100 * random.random()
        yh = 100 * random.random()
        print('creating water')
        world.create_water(lambda p: noise.pnoise2(xr + p[0] / 256, yr + p[1] / 256, 8) -
                                     0.15 * ((p[0]/self.xdim)**2 + (p[1]/self.ydim)**2),
                           -0.15)
        print('setting coast heights')
        world.set_coast_height()
        print('generating rockiness')
        world.create_rockiness(lambda p: math.exp(2.5 + 5 * noise.pnoise2(xh + p[0] / 128, yh + p[1] / 128, 8)))
        print('generating heights')
        world.generate_heights()
        print('generating depths')
        world.generate_depths()
        print('generating rivers')
        world.generate_rivers()
        print('generating humidity')
        world.generate_wetness()
        print('saving preview')
        world.save_image('preview.png')
        print('generating game trails')
        world.generate_game_trails()
        print('generating peaks')
        world.generate_peakness()
        print('generating walking costs')
        world.generate_walking_costs()
        print('generating destinations')
        world.generate_destinations(10, 10)
        print('generating hiking trails')
        world.generate_hiking_trails(500)
        print('done')
        return world


if __name__ == '__main__':
    world = WorldGenerator((800, 800), 15000).generate_world()
    #world = WorldGenerator((200, 200), 1100).generate_world()
    #world = WorldGenerator((300, 300), 2200).generate_world()
    #world = WorldGenerator((400, 400), 4500).generate_world()
    #world = WorldGenerator((500, 500), 6000).generate_world()
    print('saving')
    world.save_image()
