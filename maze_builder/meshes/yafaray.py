from .mesh import MeshBuilder
import xml.etree.ElementTree as ET


YAFARAY_INDEX_BASE = 0


def yafaray_xml_element(mesh, parent=None, material_map=None):
    """
    Returns a `xml.etree.ElementTree` compatible `<mesh>` element.  You will need to either convert this
    to a string, or incorporate into a larger XML object to use it in yafaray.
    """
    if isinstance(mesh, MeshBuilder) and mesh.index_base == YAFARAY_INDEX_BASE and material_map is None:
        prepared = mesh
    else:
        prepared = MeshBuilder(YAFARAY_INDEX_BASE)
        mesh.send_to(prepared, sort_material=True, material_map=material_map)

    kwargs = dict(
        vertices=str(len(prepared.vertices)),
        faces=str(len(prepared.faces)),
        has_uv=str(bool(prepared.texture_vertices)).lower()
    )

    if parent:
        top = ET.SubElement(parent, 'mesh', **kwargs)
    else:
        top = ET.Element('mesh', **kwargs)

    for vertex in prepared.vertices:
        ET.SubElement(top, 'p', x=vertex[0], y=vertex[1], z=vertex[2])

    for vertex in prepared.texture_vertices:
        ET.SubElement(top, 'uv', u=vertex[0], v=vertex[1])

    material = None
    for face in prepared.faces:
        if face.material and face.material != material:
            ET.SubElement(top, 'set_material', sval=face.material)
            material = face.material

        kwargs = dict(
            uv_a=face.texture_vertices[0],
            uv_b=face.texture_vertices[1],
            uv_c=face.texture_vertices[2]
        ) if face.texture_vertices else dict()

        ET.SubElement(
            top, 'f',
            a=face.vertices[0], b=face.vertices[1], c=face.vertices[2],
            **kwargs
        )

    return top

