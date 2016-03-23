from .mesh import MeshBuilder
import xml.etree.ElementTree as ET
import io
import math
from maze_builder.util import timed


YAFARAY_INDEX_BASE = 0


def dump_yafaray(fp, xml, scene, *args, verbose=1, **kwargs):
    if isinstance(xml, str):
        xml = ET.ElementTree(ET.fromstring(xml))

    root = xml.find('.')
    # Lights
    if scene.background:
        with timed(verbose, 'Inserting scene background...', 'Background inserted in {0:.3f}s'):
            insert_background(root, scene.background)
    if scene.ambience:
        with timed(verbose, 'Removing old ambiences...', 'Ambiences removed in {0:.3f}s'):
            for ambience in root.findall("integrator[@name='default']"):
                root.remove(ambience)
        with timed(verbose, 'Inserting scene ambience...', 'Ambience inserted in {0:.3f}s'):
            insert_ambience(root, scene.ambience)
    if scene.lights:
        with timed(verbose, 'Removing old lights...', 'Lights removed in {0:.3f}s'):
            for light in root.findall('light'):
                root.remove(light)
        with timed(verbose, 'Inserting scene lights...', 'Lights inserted in {0:.3f}s'):
            for light in scene.lights:
                insert_light(root, light)
    # Camera
    if scene.camera:
        with timed(verbose, 'Removing old cameras...', 'Cameras removed in {0:.3f}s'):
            for camera in root.findall('camera'):
                root.remove(camera)
        with timed(verbose, 'Inserting scene camera...', 'Camera inserted in {0:.3f}s'):
            insert_camera(root, scene.camera)
    # Action
    for i, mesh in enumerate(scene.meshes):
        with timed(verbose, 'Inserting mesh {}...'.format(i+1), 'Mesh inserted in {0:.3f}s'):
            insert_mesh(root, mesh, *args, **kwargs)

    write_kwargs = dict(encoding='utf-8', xml_declaration=True)

    if fp is None:
        with io.BytesIO() as fp:
            xml.write(fp, **write_kwargs)
            return fp.getvalue()
    else:
        xml.write(fp, **write_kwargs)


def insert_light(parent, light, default_type='pointlight'):
    light_name = 'Light{}'.format(1 + len(parent.findall('light')))

    light_type = light.type or default_type

    elem = ET.SubElement(parent, 'light', name=light_name)
    ET.SubElement(elem, 'type', sval=light_type)
    ET.SubElement(elem, 'power', fval=str(light.power))
    _insert_color(elem, 'color', light.color)

    ET.SubElement(elem, 'enabled', bval=str(light.enabled).lower())
    ET.SubElement(elem, 'cast_shadows', bval=str(light.shadows).lower())

    if 'sun' in light_type:
        _insert_location(elem, 'direction', light.location)
        ET.SubElement(elem, 'angle', fval=str(0.5))
        ET.SubElement(elem, 'samples', ival=str(16))
    else:
        _insert_location(elem, 'from', light.location)

    return elem


def insert_camera(parent, camera, default_type='perspective'):
    camera_name = 'cam' #'Camera{}'.format(1 + len(parent.findall('camera')))

    camera_type = camera.type or default_type

    elem = ET.SubElement(parent, 'camera', name=camera_name)
    ET.SubElement(elem, 'type', sval=camera_type)

    ET.SubElement(elem, 'aperture', fval='0')
    ET.SubElement(elem, 'bokeh_rotation', fval='0')
    ET.SubElement(elem, 'bokeh_type', sval='disk1')
    ET.SubElement(elem, 'dof_distance', fval='0')
    ET.SubElement(elem, 'focal', fval='1.09375')
    _insert_location(elem, 'from', camera.location)
    _insert_location(elem, 'to', camera.look_at)
    _insert_location(elem, 'up', camera.up_from_look_at)
    ET.SubElement(elem, 'view_name', sval='')
    ET.SubElement(elem, 'resx', ival=str(int(camera.resolution[0])))
    ET.SubElement(elem, 'resy', ival=str(int(camera.resolution[1])))

    return elem


def insert_mesh(parent, mesh, material_map=None):
    """
    Returns a `xml.etree.ElementTree` compatible `<mesh>` element.  You will need to either convert this
    to a string, or incorporate into a larger XML object to use it in yafaray.
    """
    index_offset = YAFARAY_INDEX_BASE - mesh.attributes.index_base

    mesh_id = '1'

    kwargs = dict(
        vertices=str(mesh.count_vertices()),
        faces=str(mesh.count_faces()),
        has_uv=str(0 < mesh.count_texture_vertices()).lower(),
        id=str(mesh_id),
        type='0',
        has_orco='false',
        obj_pass_index='0',
    )

    if parent:
        mesh_id = str(1 + len(parent.findall('mesh')))
        kwargs.update(id=mesh_id)
        top = ET.SubElement(parent, 'mesh', **kwargs)
    else:
        top = ET.Element('mesh', **kwargs)

    for vertex in mesh.iter_vertices():
        _insert_location(top, 'p', vertex, mesh.attributes.coordinate_rounding)

    for vertex in mesh.iter_texture_vertices():
        ET.SubElement(top, 'uv', u=str(vertex[0]), v=str(vertex[1]))

    material = None
    for face in mesh.iter_faces():
        face_material = material_map[face.material] if material_map else face.material
        if face_material and face_material != material:
            ET.SubElement(top, 'set_material', sval=str(face_material))
            material = face_material

        kwargs = dict(
            a=str(face.vertices[0] + index_offset),
            b=str(face.vertices[1] + index_offset),
            c=str(face.vertices[2] + index_offset),
        )
        if face.texture_vertices:
            kwargs.update(
                uv_a=str(face.texture_vertices[0] + index_offset),
                uv_b=str(face.texture_vertices[1] + index_offset),
                uv_c=str(face.texture_vertices[2] + index_offset)
            )

        ET.SubElement(top, 'f', **kwargs)

    if parent and mesh.attributes.smoothing_degrees is not None:
        ET.SubElement(
            parent, 'smooth',
            ID=mesh_id, angle=str(mesh.attributes.smoothing_degrees)
        )

    return top


def insert_ambience(parent, ambience):
    if parent:
        elem = ET.SubElement(parent, 'integrator', name='default')
    else:
        elem = ET.Element('integrator', name='default')
    _insert_color(elem, 'AO_color', ambience.color)
    ET.SubElement(elem, 'AO_distance', fval=str(ambience.distance))
    ET.SubElement(elem, 'AO_samples', ival=str(32))
    ET.SubElement(elem, 'type', sval='directlighting')
    ET.SubElement(elem, 'do_AO', bval='true')
    ET.SubElement(elem, 'bg_transp', bval='false')
    ET.SubElement(elem, 'bg_transp_refract', bval='false')
    ET.SubElement(elem, 'caustics', bval='false')
    ET.SubElement(elem, 'raydepth', ival='2')
    ET.SubElement(elem, 'shadowDepth', ival='2')
    ET.SubElement(elem, 'transpShad', bval='false')

    return elem


def insert_background(parent, background):
    created = False
    if parent:
        elem = parent.find('background')
        if elem:
            color = elem.find('color')
            if color:
                elem.remove(color)
        else:
            elem = ET.SubElement(parent, 'background', name='world_background')
            created = True
    else:
        elem = ET.Element('background', name='world_background')
        created = True

    if created:
        ET.SubElement(elem, 'ibl', bval='false')
        ET.SubElement(elem, 'ibl_samples', ival='16')
        ET.SubElement(elem, 'power', fval='1')
        ET.SubElement(elem, 'type', sval='constant')

    _insert_color(elem, 'color', background)

    return elem


def _insert_color(parent, tag, color, **kwargs):
    return ET.SubElement(parent, tag, r=str(color.r), g=str(color.g), b=str(color.b), a=str(color.a), **kwargs)


def _insert_location(parent, tag, location, rounding=None, **kwargs):
    if rounding is not None:
        location = tuple(round(c, rounding) for c in location)
    return ET.SubElement(parent, tag, x=str(location[0]), y=str(location[1]), z=str(location[2]), **kwargs)


def _insert_before(parent, path, tag, **kwargs):
    if path:
        insert_element = parent.find(path)
        index = _get_element_index(parent, insert_element)
        result = parent.makeelement(tag, kwargs.copy())
        parent.insert(index, result)
    else:
        result = ET.SubElement(parent, tag, **kwargs)
    return result


def _get_element_index(root, element):
    # http://stackoverflow.com/a/32485108/1115497
    for idx, child in enumerate(root):
        if element == child:
            return idx
    else:
        raise ValueError("No '%s' tag found in '%s' children" %
                         (element.tag, root.tag))
