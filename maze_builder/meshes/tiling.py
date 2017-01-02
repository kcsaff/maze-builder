from vertexarray import VertexArray
from maze_builder.meshes.geometry import Polygon


class Border(object):
    def __init__(self, vertices, indices, junctionlist=None):
        self.vertices = vertices
        self.indices = tuple(sorted(indices))
        self.regions = set()
        self.junctionlist = junctionlist

    @property
    def junctions(self):
        return tuple(self.junctionlist[i] for i in self.indices)

    def add_region(self, region):
        self.regions.add(region)
        return self

    def __hash__(self):
        return hash(self.indices)

    def __eq__(self, other):
        return self.indices == other.indices

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def key(self):
        return self.indices

    def other(self, not_index):
        if isinstance(not_index, Region):
            not_region = not_index
            if not_region not in self.regions:
                raise IndexError(
                    'Edge returns other region only when given region belongs to the edge: {} is not in {}'.format(
                        not_region, self.regions
                    )
                )
            for r in self.regions:
                if r is not not_region:
                    return r

        elif isinstance(not_index, Junction):
            not_junction = not_index
            not_index = not_junction.index
            if not_index not in self.indices:
                raise IndexError(
                    'Edge returns other junction only when given junction belongs to the edge: {} is not in {}'.format(
                        not_junction, self.indices
                    )
                )
            return self.junctionlist[self.indices[1] if self.indices[0] == not_index else self.indices[0]]

        else:
            if not_index not in self.indices:
                raise IndexError(
                    'Edge returns other index only when given index belongs to the edge: {} is not in {}'.format(
                        not_index, self.indices
                    )
                )

            return self.indices[1] if self.indices[0] == not_index else self.indices[0]


class Junction(object):
    def __init__(self, vertices, index):
        self.vertices = vertices
        self.index = index
        self.borders = set()
        self.regions = set()

    @property
    def vertex(self):
        return self.vertices[self.index]

    def neighbors(self):
        for border in self.borders:
            yield border.other(self)

    def add_border(self, border):
        self.borders.add(border)
        return self

    def add_region(self, region):
        self.regions.add(region)
        return self


class Region(Polygon):
    def __init__(self, vertices, indices, junctionlist=None):
        super().__init__(vertices, indices)
        self.borders = set()
        self.junctionlist = junctionlist

    def add_border(self, border):
        self.borders.add(border)

    @property
    def junctions(self):
        return (self.junctionlist[i] for i in self.indices)

    def neighbors(self):
        for border in self.borders:
            other = border.other(self)
            if other:
                yield other


class Tiling(object):
    def __init__(
            self, vertices, polygons,
            junction_class=Junction, border_class=Border, region_class=Region
    ):
        self.vertices = VertexArray(vertices)

        self.borders = dict()
        self.junctions = [junction_class(self.vertices, i) for i in range(len(self.vertices))]
        self.regions = [region_class(self.vertices, indices, self.junctions) for indices in polygons]
        for region in self.regions:
            for index in region.indices:
                self.junctions[index].add_region(region)
            for edge in region.edges_indices:
                key = tuple(sorted(edge))
                if key in self.borders:
                    border = self.borders[key]
                else:
                    border = border_class(self.vertices, edge, self.junctions)
                    self.borders[key] = border
                    for index in border.indices:
                        self.junctions[index].add_border(border)
                border.add_region(region)
                region.add_border(border)
