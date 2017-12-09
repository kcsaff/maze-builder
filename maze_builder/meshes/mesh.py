from numbers import Number
import operator
import numpy, numpy.linalg
from collections import OrderedDict, namedtuple
from vertexarray import VertexArray


Face = namedtuple('Face', ['vertices', 'texture_vertices', 'normal_vertices', 'material'])


def _scale_tuple(t0, s):
    return tuple(t*s for t in t0)


def _add_tuples(*tuples):
    return tuple(sum(item, 0) for item in zip(*tuples))


def _sub_tuples(t0, t1):
    return tuple(x0 - x1 for x0, x1 in zip(t0, t1))


def _dot_tuples(t0, t1):
    return sum(x0*x1 for x0, x1 in zip(t0, t1))


def _local_coordinates(vo, *scalar_coord_pairs):
    return tuple(
        sum((s * (v[i] - vo[i]) for s, v in scalar_coord_pairs), vo[i])
        for i in range(3)
    )


MeshAttributes = namedtuple(
    'MeshAttributes',
    ['smoothing_degrees', 'index_base', 'coordinate_rounding', 'default_material']
)


DEFAULT_MESH_ATTRIBUTES = MeshAttributes(
    smoothing_degrees=None,
    index_base=0,
    coordinate_rounding=4,
    default_material=None,
)


class MeshBase(object):
    def __init__(self, **attrs):
        self.attributes = DEFAULT_MESH_ATTRIBUTES._replace(**attrs)

    def update_attributes(self, **attrs):
        self.attributes = self.attributes._replace(**attrs)

    # Interface use-able by implementers

    def round(self, c):
        return round(c, self.attributes.coordinate_rounding)

    def round_vertex(self, v):
        rounding = self.attributes.coordinate_rounding
        return tuple(round(c, rounding) for c in v)

    def iter_vertices(self):
        for i in range(self.count_vertices()):
            yield i, self.get_vertex(self.attributes.index_base + i)

    def iter_texture_vertices(self):
        for i in range(self.count_texture_vertices()):
            yield i, self.get_texture_vertex(self.attributes.index_base + i)

    def iter_normal_vertices(self):
        for i in range(self.count_normal_vertices()):
            yield i, self.get_normal_vertex(self.attributes.index_base + i)

    def iter_faces(self):
        for i in range(self.count_faces()):
            yield self.get_face(self.attributes.index_base + i)

    def find_limits(self, coords, xbounds=None, ybounds=None, zbounds=None):
        max_limit = -float('inf')
        min_limit = float('inf')
        for _, vertex in self.iter_vertices():
            if xbounds and not xbounds[0] <= vertex[0] <= xbounds[1]:
                continue
            if ybounds and not ybounds[0] <= vertex[1] <= ybounds[1]:
                continue
            if zbounds and not zbounds[0] <= vertex[2] <= zbounds[1]:
                continue
            dot = _dot_tuples(vertex, coords)
            if dot > max_limit:
                max_limit = dot
            if dot < min_limit:
                min_limit = dot
        return min_limit, max_limit

    def force_vertices(self, vertices, fun):
        return tuple(fun(v) for v in vertices) if vertices else None

    def force_vertex_index(self, coords):
        if isinstance(coords, int):
            return coords
        else:
            return self.enter_vertex(coords)

    def force_vertex_coords(self, index):
        if isinstance(index, int):
            return self.get_vertex(index)
        else:
            return index

    def force_texture_vertex_index(self, coords):
        if isinstance(coords, int):
            return coords
        else:
            return self.enter_texture_vertex(coords)

    def force_texture_vertex_coords(self, index):
        if isinstance(index, int):
            return self.get_texture_vertex(index)
        else:
            return index

    def force_normal_vertex_index(self, coords):
        if isinstance(coords, int):
            return coords
        else:
            return self.enter_normal_vertex(coords)

    def force_normal_vertex_coords(self, index):
        if isinstance(index, int):
            return self.get_normal_vertex(index)
        else:
            return index

    # Low-ish level stuff -- necessary part of mesh interface

    def count_vertices(self):
        raise NotImplementedError

    def count_texture_vertices(self):
        raise NotImplementedError

    def count_normal_vertices(self):
        raise NotImplementedError

    def count_faces(self):
        raise NotImplementedError

    def replace_vertex(self, index, coords):
        raise NotImplementedError

    def replace_texture_vertex(self, index, coords):
        raise NotImplementedError

    def replace_normal_vertex(self, index, coords):
        raise NotImplementedError

    def enter_vertex(self, coords):
        raise NotImplementedError

    def enter_texture_vertex(self, coords):
        raise NotImplementedError

    def enter_normal_vertex(self, coords):
        raise NotImplementedError

    def get_vertex(self, index):
        raise NotImplementedError

    def get_texture_vertex(self, index):
        raise NotImplementedError

    def get_normal_vertex(self, index):
        raise NotImplementedError

    def enter_face(self, vertices, texture_vertices=None, normal_vertices=None, material=None):
        raise NotImplementedError

    def get_face(self, index):
        raise NotImplementedError

    # High-ish level stuff -- not necessary part of Mesh interface

    def perform_warp(self, warp):
        for i, v in self.iter_vertices():
            self.replace_vertex(i, warp(v))
        for i, v in self.iter_normal_vertices():
            self.replace_normal_vertex(i, warp(v))
        return self

    def triangle(self, vertices, texture_vertices=None, density=1, material=None):
        """
        Note: v0, v1 are ABSOLUTE to vo; likewise with t0, t1 ABSOLUTE to to
        """
        vo, v0, v1 = tuple(self.force_vertex_coords(v) for v in vertices)
        vs = [
            [self.force_vertex_index(_local_coordinates(vo, (i/density, v0), (j/density, v1)))
             for j in range(density+1-i)]
            for i in range(density+1)
        ]
        if texture_vertices:
            to, t0, t1 = tuple(self.force_texture_vertex_coords(t) for t in texture_vertices)
            vts = [
                [self.force_texture_vertex_index(_local_coordinates(to, (i/density, t0), (j/density, t1)))
                 for j in range(density+1-i)]
                for i in range(density+1)
            ]
        else:
            vts = None
        for i in range(density):
            for j in range(density-i):
                self.enter_face(
                    (vs[i][j], vs[i+1][j], vs[i][j+1]),
                    (vts[i][j], vts[i+1][j], vts[i][j+1]) if vts else None,
                )
                if i+j+1 < density:
                    self.enter_face(
                        (vs[i+1][j], vs[i+1][j+1], vs[i][j+1]),
                        (vts[i+1][j], vts[i+1][j+1], vts[i][j+1]) if vts else None,
                    )
        return self

    def rectangle(self, vertices, texture_vertices=None, density=1, material=None):
        vo, v0, v1 = tuple(self.force_vertex_coords(v) for v in vertices)
        vs = [
            [self.force_vertex_index(_local_coordinates(vo, (i/density, v0), (j/density, v1)))
             for j in range(density+1)]
            for i in range(density+1)
        ]
        if texture_vertices:
            to, t0, t1 = tuple(self.force_texture_vertex_coords(t) for t in texture_vertices)
            vts = [
                [self.force_texture_vertex_index(_local_coordinates(to, (i/density, t0), (j/density, t1)))
                 for j in range(density+1)]
                for i in range(density+1)
            ]
        else:
            vts = None
        for i in range(density):
            for j in range(density):
                self.enter_face(
                    (vs[i][j], vs[i+1][j], vs[i][j+1]),
                    (vts[i][j], vts[i+1][j], vts[i][j+1]) if vts else None,
                )
                self.enter_face(
                    (vs[i+1][j], vs[i+1][j+1], vs[i][j+1]),
                    (vts[i+1][j], vts[i+1][j+1], vts[i][j+1]) if vts else None,
                )
        return self

    def cuboid(self, vertices, texture_vertices=None, density=1, material=None):
        vo, v0, v1, v2 = tuple(self.force_vertex_coords(v) for v in vertices)
        self.rectangle((vo, v0, v1), texture_vertices, density, material)
        self.rectangle((vo, v1, v2), texture_vertices, density, material)
        self.rectangle((vo, v2, v0), texture_vertices, density, material)

        v01 = _local_coordinates(vo, v0, v1)
        v12 = _local_coordinates(vo, v1, v2)
        v20 = _local_coordinates(vo, v2, v0)

        self.rectangle((v0, v20, v01), texture_vertices, density, material)
        self.rectangle((v1, v01, v12), texture_vertices, density, material)
        self.rectangle((v2, v12, v20), texture_vertices, density, material)
        return self


class MeshBuilder(MeshBase):
    def __init__(self, **attrs):
        super().__init__(**attrs)

        self.vertices = VertexArray(ndigits=self.attributes.coordinate_rounding)
        self.texture_vertices = VertexArray(ndigits=self.attributes.coordinate_rounding)
        self.normal_vertices = VertexArray(ndigits=self.attributes.coordinate_rounding)

        self.faces = list()

        self.materials = dict()

    # Override

    def perform_warp(self, warp):
        self.vertices.warp(warp)
        self.normal_vertices.warp(warp)
        return self

    # Low-ish level stuff -- necessary part of mesh interface

    def count_vertices(self):
        return len(self.vertices)

    def count_texture_vertices(self):
        return len(self.texture_vertices)

    def count_normal_vertices(self):
        return len(self.normal_vertices)

    def count_faces(self):
        return len(self.faces)

    def enter_vertex(self, coords):
        return self._enter_vertex(coords, self.vertices)

    def enter_texture_vertex(self, coords):
        return self._enter_vertex(coords, self.texture_vertices)

    def enter_normal_vertex(self, coords):
        return self._enter_vertex(coords, self.normal_vertices)

    def get_vertex(self, index):
        return self._get_vertex(index, self.vertices)

    def get_texture_vertex(self, index):
        return self._get_vertex(index, self.texture_vertices)

    def get_normal_vertex(self, index):
        return self._get_vertex(index, self.normal_vertices)

    def replace_vertex(self, index, coords):
        return self._replace_vertex(index, coords, self.vertices)

    def replace_texture_vertex(self, index, coords):
        raise self._replace_vertex(index, coords, self.texture_vertices)

    def replace_normal_vertex(self, index, coords):
        raise self._replace_vertex(index, coords, self.normal_vertices)

    def enter_face(self, vertices,
                   texture_vertices=None, normal_vertices=None, material=None):
        self.faces.append(Face(
            tuple(self.force_vertex_index(v) for v in vertices),
            tuple(self.force_texture_vertex_index(v) for v in texture_vertices) if texture_vertices else None,
            tuple(self.force_normal_vertex_index(v) for v in normal_vertices) if normal_vertices else None,
            material.name if material else self.attributes.default_material,
        ))
        if material and material.name not in self.materials:
            self.materials[material.name] = material

    def get_face(self, index):
        return self.faces[index - self.attributes.index_base]

    # Internal

    def _replace_vertex(self, index, coords, vl):
        vl[index - self.attributes.index_base] = coords

    def _get_vertex(self, index, vl):
        if isinstance(index, int) and 0 <= index - self.attributes.index_base < len(vl):
            return vl[index - self.attributes.index_base]
        else:
            return vl[vl.enter(index)]

    def _enter_vertex(self, coords, vl):
        if isinstance(coords, int) and 0 <= coords - self.attributes.index_base < len(vl):
            return coords
        else:
            return self.attributes.index_base + vl.append(coords)


class MeshWarp(MeshBase):
    def __init__(self, mesh, warp_out=None, warp_in=None):
        self.mesh = mesh

        self.warp_out, self.warp_in = warp_out, warp_in

    @property
    def attributes(self):
        return self.mesh.attributes

    def update_attributes(self, **attrs):
        self.mesh.update_attributes(**attrs)

    # Low-ish level stuff -- necessary part of mesh interface

    def count_vertices(self):
        return self.mesh.count_vertices()

    def count_texture_vertices(self):
        return self.mesh.count_texture_vertices()

    def count_normal_vertices(self):
        return self.mesh.count_normal_vertices()

    def count_faces(self):
        return self.mesh.count_faces()

    def enter_vertex(self, coords):
        return self.mesh.enter_vertex(self._in(coords))

    def enter_texture_vertex(self, coords):
        return self.mesh.enter_texture_vertex(coords)

    def enter_normal_vertex(self, coords):
        return self.mesh.enter_normal_vertex(self._in(coords))

    def get_vertex(self, index):
        return self._out(self.mesh.get_vertex(index))

    def get_texture_vertex(self, index):
        return self.mesh.get_texture_vertex(index)

    def get_normal_vertex(self, index):
        return self._out(self.mesh.get_normal_vertex(index))

    def enter_face(self, vertices, texture_vertices=None, normal_vertices=None, material=None):
        self.mesh.enter_face(
            self.force_vertices(vertices, self.force_vertex_index),
            self.force_vertices(texture_vertices, self.force_texture_vertex_index),
            self.force_vertices(normal_vertices, self.force_normal_vertex_index),
            material,
        )

    def get_face(self, index):
        return self.mesh.get_face(index)

    # Internal
    def _in(self, vertex):
        return tuple(self.warp_in(vertex))

    def _out(self, vertex):
        return tuple(self.warp_out(vertex))


class MeshTransformation(MeshWarp):
    def __init__(self, mesh, transform_out=None, transform_in=None):
        transform_out = numpy.matrix(transform_out) if transform_out is not None else None
        transform_in = numpy.matrix(transform_in) if transform_in is not None else None

        if transform_in is None and transform_out is None:
            transform_in = numpy.identity(3)
            transform_out = numpy.identity(3)
        elif transform_in is None:
            try:
                transform_in = numpy.linalg.inv(transform_out)
            except:
                transform_in = None
        elif transform_out is None:
            try:
                transform_out = numpy.linalg.inv(transform_in)
            except:
                transform_out = None

        self.transform_out, self.transform_in = transform_out, transform_in

        super().__init__(
            mesh,
            warp_in=lambda vertex: self.transform_in.dot(vertex).tolist()[0][:3] if self.transform_in else None,
            warp_out=lambda vertex: self.transform_out.dot(vertex).tolist()[0][:3] if self.transform_out else None,
        )


if __name__ == '__main__':
    mesh = MeshBuilder()
    mesh.triangle(((0,0,1), (4,0,1), (0,2,1)), density=2)
    for face in mesh.faces:
        print(tuple(mesh.get_vertex(v) for v in face.vertices))
