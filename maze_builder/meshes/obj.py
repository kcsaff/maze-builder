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

    def _format_face(self, face, index_offset):
        svs = tuple(str(v + index_offset) for v in face.vertices)
        if face.normal_vertices and 'vn' in self.keywords:
            svts = tuple(str(v + index_offset) for v in face.texture_vertices) if face.texture_vertices else tuple('' for _ in face.vertices)
            svns = tuple(str(v + index_offset) for v in face.normal_vertices)
            return tuple('/'.join(triplet) for triplet in zip(svs, svts, svns))
        elif face.texture_vertices and 'vt' in self.keywords:
            svts = tuple(str(v + index_offset) for v in face.texture_vertices)
            return tuple('/'.join(triplet) for triplet in zip(svs, svts))
        else:
            return svs

    def dump(self, fp, mesh):
        index_offset = OBJ_INDEX_BASE - mesh.attributes.index_base

        for _, vertex in mesh.iter_vertices():
            self.write(fp, 'v', *vertex)

        for _, vertex in mesh.iter_texture_vertices():
            self.write(fp, 'vt', *vertex)

        for _, vertex in mesh.iter_normal_vertices():
            self.write(fp, 'vn', *vertex)

        material = None
        for face in mesh.iter_faces():
            if face.material and face.material != material:
                self.write(fp, 'usemtl', face.material)
                material = face.material
            self.write(fp, 'f', *self._format_face(face, index_offset))


def dump_obj(fp, mesh):
    """
    Returns a `xml.etree.ElementTree` compatible `<mesh>` element.  You will need to either convert this
    to a string, or incorporate into a larger XML object to use it in yafaray.
    """
    if fp is None:
        with StringIO() as fp:
            ObjDumper().dump(fp, mesh)
            return fp.getvalue()
    elif isinstance(fp, str):
        with open(fp, 'w') as f:
            ObjDumper().dump(f, mesh)
    else:
        ObjDumper().dump(fp, mesh)
