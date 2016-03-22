from numbers import Number
import operator
import numpy, numpy.linalg
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


MeshAttributes = namedtuple('MeshAttributes', ['smoothing_degrees'])


DEFAULT_MESH_ATTRIBUTES = MeshAttributes(
    smoothing_degrees=None,
)


class MeshBase(object):
    def __init__(self, mesh=None, **attrs):
        if mesh:
            if attrs:
                raise RuntimeError('Cannot set wrapped mesh & attributes')
            self.mesh = mesh  # Wrapped mesh, if any
        else:
            self.mesh = None
            self.attributes = DEFAULT_MESH_ATTRIBUTES._replace(**attrs)

    def get_attributes(self):
        return self.mesh.attributes if self.mesh else self.attributes

    def update_attributes(self, **attrs):
        if self.mesh:
            self.mesh.update_attributes(**attrs)
        else:
            self.attributes = self.attributes._replace(**attrs)

    # For exporting and conversions

    def send_to(self, mesh, sort_material=False, material_map=None):
        raise NotImplementedError

    # High-ish level stuff -- not necessary part of Mesh interface
    
    def triangle(self, vertices, texture_vertices=None, density=1, material=None):
        """
        Note: v0, v1 are ABSOLUTE to vo; likewise with t0, t1 ABSOLUTE to to
        """
        vo, v0, v1 = tuple(self.force_vertex_coords(v) for v in vertices)
        has_textures = bool(texture_vertices)
        if has_textures:
            to, t0, t1 = tuple(self.force_texture_vertex_coords(v) for v in texture_vertices)
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
                self.face(dv, dt, material=material)
    
    def rectangle(self, vertices, texture_vertices=None, density=1, material=None):
        self.triangle(vertices, texture_vertices, density=density, material=material)

        # Reversed triangle
        vo, v0, v1 = tuple(self.force_vertex_coords(v) for v in vertices)
        if texture_vertices:
            to, t0, t1 = tuple(self.force_texture_vertex_coords(t) for t in texture_vertices)
        self.triangle(
            (_local_coordinates(vo, (1, v0), (1, v1)), v1, v0),
            (_local_coordinates(to, (1, t0), (1, t1)), t1, t0) if texture_vertices else None,
            density=density,
            material=material
        )
        return self

    # Interface use-able by implementers

    def force_vertices(self, vertices, fun):
        return tuple(fun(v) for v in vertices) if vertices else None

    def force_vertex_index(self, coords):
        if isinstance(coords, int):
            return coords
        else:
            return self.vertex(coords)

    def force_vertex_coords(self, index):
        if isinstance(index, int):
            return self.get_vertex(index)
        else:
            return index

    def force_texture_vertex_index(self, coords):
        if isinstance(coords, int):
            return coords
        else:
            return self.texture_vertex(coords)

    def force_texture_vertex_coords(self, index):
        if isinstance(index, int):
            return self.get_texture_vertex(index)
        else:
            return index

    def force_normal_vertex_index(self, coords):
        if isinstance(coords, int):
            return coords
        else:
            return self.normal_vertex(coords)

    def force_normal_vertex_coords(self, index):
        if isinstance(index, int):
            return self.get_normal_vertex(index)
        else:
            return index

    # Low-ish level stuff -- necessary part of mesh interface

    def vertex(self, coords):
        raise NotImplementedError

    def texture_vertex(self, coords):
        raise NotImplementedError

    def normal_vertex(self, coords):
        raise NotImplementedError

    def get_vertex(self, index):
        raise NotImplementedError

    def get_texture_vertex(self, index):
        raise NotImplementedError

    def get_normal_vertex(self, index):
        raise NotImplementedError

    def face(self, vertices, texture_vertices=None, normal_vertices=None, material=None):
        raise NotImplementedError


class MeshBuilder(MeshBase):
    def __init__(self, index_base=0, rounding=4, **attrs):
        super().__init__(**attrs)
        self.index_base = index_base
        self.rounding = rounding

        self.vertex_lookup = OrderedDict()
        self.texture_vertex_lookup = OrderedDict()
        self.normal_vertex_lookup = OrderedDict()

        self.vertices = list()
        self.texture_vertices = list()
        self.normal_vertices = list()

        self.faces = list()

    # For exporting and conversions

    def send_to(self, mesh, sort_material=False, material_map=None):
        mesh.update_attributes(**vars(self.get_attributes()))

        local_vertex_lookup = dict()
        local_texture_vertex_lookup = dict()
        local_normal_vertex_lookup = dict()

        for vertex, index in self.vertex_lookup.items():
            local_vertex_lookup[index] = mesh.vertex(vertex)
        for texture_vertex, index in self.texture_vertex_lookup.items():
            local_texture_vertex_lookup[index] = mesh.texture_vertex(texture_vertex)
        for normal_vertex, index in self.normal_vertex_lookup.items():
            local_normal_vertex_lookup[index] = mesh.normal_vertex(normal_vertex)

        if sort_material:
            self.faces.sort(key=lambda face: face.material or '')

        for face in self.faces:
            mesh.face(
                self.force_vertices(face.vertices, local_vertex_lookup.__getitem__),
                self.force_vertices(face.texture_vertices, local_texture_vertex_lookup.__getitem__),
                self.force_vertices(face.normal_vertices, local_normal_vertex_lookup.__getitem__),
                material_map[face.material] if material_map else face.material,
            )

    # Low-ish level stuff -- necessary part of mesh interface

    def vertex(self, coords):
        return self._enter_vertex(coords, self.vertex_lookup, self.vertices)

    def texture_vertex(self, coords):
        return self._enter_vertex(coords, self.texture_vertex_lookup, self.texture_vertices)

    def normal_vertex(self, coords):
        return self._enter_vertex(coords, self.normal_vertex_lookup, self.normal_vertices)

    def get_vertex(self, index):
        return self._get_vertex(index, self.vertex_lookup, self.vertices)

    def get_texture_vertex(self, index):
        return self._get_vertex(index, self.texture_vertex_lookup, self.texture_vertices)

    def get_normal_vertex(self, index):
        return self._get_vertex(index, self.normal_vertex_lookup, self.normal_vertices)

    def face(self, vertices, texture_vertices=None, normal_vertices=None, material=None):
        self.faces.append(Face(
            tuple(self.force_vertex_index(v) for v in vertices),
            tuple(self.force_texture_vertex_index(v) for v in texture_vertices) if texture_vertices else None,
            tuple(self.force_normal_vertex_index(v) for v in normal_vertices) if normal_vertices else None,
            material,
        ))

    # Internal

    def _get_vertex(self, index, d, L):
        if isinstance(index, int) and 0 <= index - self.index_base < len(d):
            return L[index - self.index_base]
        else:
            return L[self._enter_vertex(index, d, L)]

    def _enter_vertex(self, coords, d, L):
        if isinstance(coords, int) and 0 <= coords - self.index_base < len(d):
            return coords
        else:
            coords = tuple(round(c, self.rounding) for c in coords)
            index = d.get(coords, None)

        if index is None:
            index = self.index_base + len(d)
            d[coords] = index
            L.append(coords)
        return index


SWAP_YZ = numpy.matrix([[1, 0, 0], [0, 0, 1], [0, 1, 0]])


class MeshTransformation(MeshBase):
    def __init__(self, mesh, transform_out=None, transform_in=None):
        super().__init__(mesh)

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

    @classmethod
    def swap_y_z(cls, mesh):
        return cls(mesh, transform_in=SWAP_YZ, transform_out=SWAP_YZ)

    # For exporting and conversions

    def send_to(self, mesh, *args, **kwargs):
        self.mesh.send_to(self.invert(mesh), *args, **kwargs)

    # High-ish level stuff -- not necessary part of Mesh interface

    def invert(self, mesh=None):
        return MeshTransformation(mesh or self.mesh, transform_in=self.transform_out, transform_out=self.transform_in)

    # Low-ish level stuff -- necessary part of mesh interface

    def vertex(self, coords):
        if isinstance(coords, int):  # Actually index
            return coords
        else:
            return self.mesh.vertex(self._in(coords))

    def texture_vertex(self, coords):
        return self.mesh.vertex(coords)

    def normal_vertex(self, coords):
        return self.mesh.normal_vertex(self._in(coords))

    def get_vertex(self, index):
        if isinstance(index, int):
            return self._out(self.mesh.get_vertex(index))
        else:  # Actually coords
            self.mesh.vertex(self._in(index))
            return index

    def get_texture_vertex(self, index):
        return self.mesh.get_vertex(index)

    def get_normal_vertex(self, index):
        return self._out(self.mesh.get_normal_vertex(index))

    def face(self, vertices, texture_vertices=None, normal_vertices=None, material=None):
        self.mesh.face(
            self._ins(vertices),
            texture_vertices,
            self._ins(normal_vertices),
            material,
        )

    # Internal
    def _in(self, vertex):
        return tuple(self.transform_in.dot(vertex).tolist()[0])

    def _ins(self, vertices):
        return tuple(self._in(v) for v in vertices) if vertices else None

    def _out(self, vertex):
        return tuple(self.transform_out.dot(vertex).tolist()[0])


class MeshWarp(MeshBase):

    def __init__(self, mesh, warp_out=None, warp_in=None):
        super().__init__(mesh)
        self.mesh = mesh

        self.warp_out, self.warp_in = warp_out, warp_in

    # For exporting and conversions

    def send_to(self, mesh, *args, **kwargs):
        self.mesh.send_to(self.invert(mesh), *args, **kwargs)

    # High-ish level stuff -- not necessary part of Mesh interface

    def invert(self, mesh=None):
        return MeshWarp(mesh or self.mesh, warp_out=self.warp_in, warp_in=self.warp_out)

    # Low-ish level stuff -- necessary part of mesh interface

    def vertex(self, coords):
        return self.mesh.vertex(self._in(coords))

    def texture_vertex(self, coords):
        return self.mesh.vertex(coords)

    def normal_vertex(self, coords):
        return self.mesh.normal_vertex(self._in(coords))

    def get_vertex(self, index):
        return self._out(self.mesh.get_vertex(index))

    def get_texture_vertex(self, index):
        return self.mesh.get_vertex(index)

    def get_normal_vertex(self, index):
        return self._out(self.mesh.get_normal_vertex(index))

    def face(self, vertices, texture_vertices=None, normal_vertices=None, material=None):
        self.mesh.face(
            self.force_vertices(vertices, self.force_vertex_index),
            self.force_vertices(texture_vertices, self.force_texture_vertex_index),
            self.force_vertices(normal_vertices, self.force_normal_vertex_index),
            material,
        )

    # Internal
    def _in(self, vertex):
        return tuple(self.warp_in(vertex))

    def _ins(self, vertices):
        return tuple(self._in(v) for v in vertices) if vertices else None

    def _out(self, vertex):
        return tuple(self.warp_out(vertex))


if __name__ == '__main__':
    mesh = MeshBuilder()
    mesh.triangle(((0,0,1), (4,0,1), (0,2,1)), density=2)
    for face in mesh.faces:
        print(tuple(mesh.get_vertex(v) for v in face.vertices))
