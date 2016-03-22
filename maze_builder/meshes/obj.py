from .mesh import MeshBuilder
import xml.etree.ElementTree as ET
from io import StringIO

OBJ_INDEX_BASE = 1


class ObjDumper(object):
    def __init__(self, keywords=('v', 'vt', 'vn', 'f', 'usemtl')):
        self.keywords = set(keywords)

    def write(self, fp, keyword, *args):
        if keyword in self.keywords:
            fp.write('{} {}\n'.format(keyword, ' '.join(str(arg) for arg in args)))

    def _format_face(self, face):
        svs = tuple(str(v) for v in face.vertices)
        if face.normal_vertices and 'vn' in self.keywords:
            svts = tuple(str(v) for v in face.texture_vertices) if face.texture_vertices else tuple('' for _ in face.vertices)
            svns = tuple(str(v) for v in face.normal_vertices)
            return tuple('/'.join(triplet) for triplet in zip(svs, svts, svns))
        elif face.texture_vertices and 'vt' in self.keywords:
            svts = tuple(str(v) for v in face.texture_vertices)
            return tuple('/'.join(triplet) for triplet in zip(svs, svts))
        else:
            return svs

    def dump(self, fp, mesh):
        if isinstance(mesh, MeshBuilder) and mesh.index_base == OBJ_INDEX_BASE:
            prepared = mesh
        else:
            prepared = MeshBuilder(OBJ_INDEX_BASE)
            mesh.send_to(prepared)

        for vertex in prepared.vertices:
            self.write(fp, 'v', *vertex)

        for vertex in prepared.texture_vertices:
            self.write(fp, 'vt', *vertex)

        for vertex in prepared.normal_vertices:
            self.write(fp, 'vn', *vertex)

        material = None
        for face in prepared.faces:
            if face.material and face.material != material:
                self.write(fp, 'usemtl', face.material)
                material = face.material
            self.write(fp, 'f', *self._format_face(face))


def dump_obj(fp, mesh):
    """
    Returns a `xml.etree.ElementTree` compatible `<mesh>` element.  You will need to either convert this
    to a string, or incorporate into a larger XML object to use it in yafaray.
    """
    if fp is not None:
        ObjDumper().dump(fp, mesh)
    else:
        with StringIO() as fp:
            ObjDumper().dump(fp, mesh)
            return fp.getvalue()
