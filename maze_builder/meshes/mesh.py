from numbers import Number
import operator
from collections import OrderedDict, namedtuple


Face = namedtuple('Face', ['vertices', 'texture_vertices', 'normal_vertices', 'material'])


def _scale_tuple(t0, s):
    return tuple(t*s for t in t0)


def _add_tuples(*tuples):
    return tuple(sum(item, 0) for item in zip(*tuples))


def _sub_tuples(t0, t1):
    return tuple(x0 - x1 for x0, x1 in zip(t0, t1))


def _local_coordinates(vo, *scalar_coord_pairs):
    return tuple(
        sum((s * (v[i] - vo[i]) for s, v in scalar_coord_pairs), vo[i])
        for i in range(3)
    )


class MeshBuilder(object):
    def __init__(self, index_base=0):
        self.index_base = index_base

        self.vertices = OrderedDict()
        self.texture_vertices = OrderedDict()
        self.normal_vertices = OrderedDict()

        self.vertex_list = list()
        self.texture_vertex_list = list()
        self.normal_vertex_list = list()

        self.faces = list()

    # For exporting and conversions

    def send_to(self, builder, sort_material=False, material_map=None):
        local_vertices = dict()
        local_texture_vertices = dict()
        local_normal_vertices = dict()

        for vertex, index in self.vertices.items():
            local_vertices[index] = builder.vertex(vertex)
        for texture_vertex in self.texture_vertices:
            local_texture_vertices[index] = builder.texture_vertex(texture_vertex)
        for normal_vertex in self.normal_vertices:
            local_normal_vertices[index] = builder.normal_vertex(normal_vertex)

        if sort_material:
            self.faces.sort(key=lambda face: face.material)

        for face in self.faces:
            builder.face(
                tuple(local_vertices[c] for c in face.vertices) if face.vertices else None,
                tuple(local_texture_vertices[c] for c in face.texture_vertices) if face.texture_vertices else None,
                tuple(local_normal_vertices[c] for c in face.normal_vertices) if face.normal_vertices else None,
                material_map[face.material] if material_map else face.material,
            )

    # High-ish level stuff

    def triangle(self, vertices, texture_vertices=None, density=1, material=None):
        """
        Note: v0, v1 are ABSOLUTE to vo; likewise with t0, t1 ABSOLUTE to to
        """
        vo, v0, v1 = tuple(self.get_vertex(v) for v in vertices)
        has_textures = bool(texture_vertices)
        if has_textures:
            to, t0, t1 = tuple(self.get_vertex(v) for v in texture_vertices)
        for i in range(density):
            di = i / density
            di1 = (i + 1) / density
            for j in range(density):
                dj = j / density
                dj1 = (j + 1) / density
                overage = di + dj - 1
                if overage < 0:
                    dvo = _local_coordinates(vo, (di, v0), (dj, v1))
                    dv0 = _local_coordinates(vo, (di1, v0), (dj, v1))
                    dv1 = _local_coordinates(vo, (di, v0), (dj1, v1))
                    dv = (dvo, dv0, dv1)
                    if has_textures:
                        dto = _local_coordinates(to, (di, t0), (dj, t1))
                        dt0 = _local_coordinates(to, (di1, t0), (dj, t1))
                        dt1 = _local_coordinates(to, (di, t0), (dj1, t1))
                        dt = (dto, dt0, dt1)
                    else:
                        dt = None
                else:
                    dvo = _local_coordinates(vo, (1-dj, v0), (1-di, v1))
                    dv0 = _local_coordinates(vo, (1-dj1, v0), (1-di, v1))
                    dv1 = _local_coordinates(vo, (1-dj, v0), (1-di1, v1))
                    dv = (dvo, dv0, dv1)
                    if has_textures:
                        dto = _local_coordinates(to, (1-dj, t0), (1-di, t1))
                        dt0 = _local_coordinates(to, (1-dj1, t0), (1-di, t1))
                        dt1 = _local_coordinates(to, (1-dj, t0), (1-di1, t1))
                        dt = (dto, dt0, dt1)
                    else:
                        dt = None
                print((i, j, di, dj, dv))
                self.face(dv, dt, material=material)
        return self

    def rectangle(self, vertices, texture_vertices=None, density=1, material=None):
        self.triangle(vertices, texture_vertices, density=density, material=material)

        # Reversed triangle
        vo, v0, v1 = tuple(self.get_vertex(v) for v in vertices)
        if texture_vertices:
            to, t0, t1 = tuple(self.get_vertex(t) for t in texture_vertices)
        self.triangle(
            (_local_coordinates(vo, (1, v0), (1, v1)), v1, v0),
            (_local_coordinates(to, (1, t0), (1, t1)), t1, t0) if texture_vertices else None,
            density=density,
            material=material
        )
        return self

    # Low-ish level stuff

    def vertex(self, coords):
        return self._enter_vertex(coords, self.vertices, self.vertex_list)

    def texture_vertex(self, coords):
        return self._enter_vertex(coords, self.texture_vertices, self.texture_vertex_list)

    def normal_vertex(self, coords):
        return self._enter_vertex(coords, self.normal_vertices, self.normal_vertex_list)

    def get_vertex(self, index):
        return self._get_vertex(index, self.vertices, self.vertex_list)

    def get_texture_vertex(self, index):
        return self._get_vertex(index, self.texture_vertices, self.texture_vertex_list)

    def get_normal_vertex(self, index):
        return self._get_vertex(index, self.normal_vertices, self.normal_vertex_list)

    def face(self, vertices, texture_vertices=None, normal_vertices=None, material=None):
        self.faces.append(Face(
            self._enter_vertices(vertices, self.vertices, self.vertex_list),
            self._enter_vertices(texture_vertices, self.texture_vertices, self.texture_vertex_list),
            self._enter_vertices(normal_vertices, self.normal_vertices, self.normal_vertex_list),
            material,
        ))

    def _enter_vertices(self, vertices, d, L):
        return tuple(self._enter_vertex(v, d, L) for v in vertices) if vertices else None

    def _get_vertex(self, index, d, L):
        if isinstance(index, int) and 0 <= index - self.index_base < len(d):
            return L[index - self.index_base]
        else:
            return L[self._enter_vertex(index, d, L)]

    def _enter_vertex(self, coords, d, L):
        if isinstance(coords, int) and 0 <= coords - self.index_base < len(d):
            return coords
        else:
            index = d.get(coords, None)

        if index is None:
            index = self.index_base + len(d)
            d[coords] = index
            L.append(coords)
        return index


if __name__ == '__main__':
    mesh = MeshBuilder()
    mesh.triangle(((0,0,1), (4,0,1), (0,2,1)), density=2)
    for face in mesh.faces:
        print(tuple(mesh.get_vertex(v) for v in face.vertices))
