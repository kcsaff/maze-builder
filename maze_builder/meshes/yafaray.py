from .mesh import MeshBuilder
import xml.etree.ElementTree as ET
import io
import math


YAFARAY_INDEX_BASE = 0


def dump_yafaray(fp, mesh, xml, *args, **kwargs):
    out = make_yafaray_xml(mesh, xml, *args, **kwargs)

    write_kwargs = dict(encoding='utf-8', xml_declaration=True)

    if fp is None:
        with io.BytesIO() as fp:
            out.write(fp, **write_kwargs)
            return fp.getvalue()
    else:
        out.write(fp, **write_kwargs)


def make_yafaray_xml(mesh, xml, *args, **kwargs):
    if isinstance(xml, str):
        xml = ET.ElementTree(ET.fromstring(xml))
    make_yafaray_mesh(mesh, xml.find('.'), *args, **kwargs)
    return xml


def _insert_before(parent, path, tag, **kwargs):
    if path:
        insert_element = parent.find(path)
        index = _get_element_index(parent, insert_element)
        result = parent.makeelement(tag, kwargs.copy())
        parent.insert(index, result)
    else:
        result = ET.SubElement(parent, tag, **kwargs)
    return result


def make_yafaray_mesh(mesh, parent=None, material_map=None, insert_before='camera'):
    """
    Returns a `xml.etree.ElementTree` compatible `<mesh>` element.  You will need to either convert this
    to a string, or incorporate into a larger XML object to use it in yafaray.
    """
    if isinstance(mesh, MeshBuilder) and mesh.index_base == YAFARAY_INDEX_BASE and material_map is None:
        prepared = mesh
    else:
        prepared = MeshBuilder(YAFARAY_INDEX_BASE)
        mesh.send_to(prepared, sort_material=True, material_map=material_map)

    mesh_id = '1'

    kwargs = dict(
        vertices=str(len(prepared.vertices)),
        faces=str(len(prepared.faces)),
        has_uv=str(bool(prepared.texture_vertices)).lower(),
        id=mesh_id,
        type='0',
        has_orco='false',
        obj_pass_index='0',
    )

    if parent:
        mesh_id = str(1 + len(parent.findall('mesh')))
        kwargs.update(id=mesh_id)
        top = _insert_before(parent, insert_before, 'mesh', **kwargs)
    else:
        top = ET.Element('mesh', **kwargs)

    for vertex in prepared.vertices:
        ET.SubElement(top, 'p', x=str(vertex[0]), y=str(vertex[1]), z=str(vertex[2]))

    for vertex in prepared.texture_vertices:
        ET.SubElement(top, 'uv', u=str(vertex[0]), v=str(vertex[1]))

    material = None
    for face in prepared.faces:
        if face.material and face.material != material:
            ET.SubElement(top, 'set_material', sval=str(face.material))
            material = face.material

        kwargs = dict(
            uv_a=str(face.texture_vertices[0]),
            uv_b=str(face.texture_vertices[1]),
            uv_c=str(face.texture_vertices[2])
        ) if face.texture_vertices else dict()

        ET.SubElement(
            top, 'f',
            a=str(face.vertices[0]), b=str(face.vertices[1]), c=str(face.vertices[2]),
            **kwargs
        )

    if parent and mesh.get_attributes().smoothing_degrees is not None:
        _insert_before(
            parent, insert_before, 'smooth',
            ID=mesh_id, angle=str(mesh.get_attributes().smoothing_degrees)
        )

    return top


def _get_element_index(root, element):
    # http://stackoverflow.com/a/32485108/1115497
    for idx, child in enumerate(root):
        if element == child:
            return idx
    else:
        raise ValueError("No '%s' tag found in '%s' children" %
                         (element.tag, root.tag))
