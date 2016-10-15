from collections import namedtuple
from contextlib import contextmanager
from .mesh import MeshBuilder
import xml.etree.ElementTree as ET
import io
import math
import xmlwitch
from maze_builder.util import timed, is_verbose


YAFARAY_INDEX_BASE = 0


class Element(object):
    __slots__ = ('tag', 'text', 'tail', '_attrib', '_children')

    def __init__(self, tag, text=None, tail=None, **attrib):
        self.tag = tag
        self.text = text
        self.tail = tail
        self._attrib = attrib or None
        self._children = None

    def __iter__(self):
        yield from self.children

    @property
    def attrib(self):
        return self._attrib or {}

    @property
    def children(self):
        children = self._children or ()
        if callable(children):
            children = children()
        return children

    @property
    def has_children(self):
        return callable(self._children) or self._children

    def find(self, tag, **attrib):
        for child in self:
            if matches(child, tag, **attrib):
                return child
        else:
            return None

    def findall(self, tag, **attrib):
        return [child for child in self if matches(child, tag, **attrib)]

    def remove_all(self, tag, **attrib):
        self._children = [
            child for child in self if not matches(child, tag, **attrib)
        ]

    def generate(self, fun):
        if self._children is not None:
            raise RuntimeError('Cannot add generator to actual children')

        self._children = fun
        return fun

    def child(self, tag, text=None, tail=None, **attrib):
        self._make_children()
        child = Element(tag, text, tail, **attrib)
        self._children.append(child)
        return child

    def extend(self, children):
        self._make_children()
        self._children.extend(children)

    def _make_children(self):
        if self._children is None:
            self._children = list()
        elif not isinstance(self._children, list):
            raise 'Cannot add child to generator'

    @classmethod
    def deepcopy(cls, element):
        copied = cls(element.tag, element.text, element.tail, **element.attrib)
        copied.extend(cls.deepcopy(child) for child in element)
        return copied

    def write(self, witch):
        el = witch[self.tag](self.text, **self.attrib)
        if self.has_children:
            with el:
                for child in self:
                    child.write(witch)


def matches(child, tag, **attrib):
    if tag is not None and child.tag != tag:
        return False
    for key, value in attrib.items():
        if (child.attrib or {}).get(key) != value:
            return False
    return True



def dump_yafaray(filename, xml, scene, *args, **kwargs):
    root = Element.deepcopy(ET.fromstring(xml))

    # Lights
    if scene.background:
        with timed(is_verbose(2), 'Inserting scene background...', 'Background inserted in {0:.3f}s'):
            insert_background(root, scene.background)
    if scene.ambience:
        with timed(is_verbose(2), 'Removing old ambiences...', 'Ambiences removed in {0:.3f}s'):
            root.remove_all('integrator', name='default')
        with timed(is_verbose(2), 'Inserting scene ambience...', 'Ambience inserted in {0:.3f}s'):
            insert_ambience(root, scene.ambience)
    if scene.lights:
        with timed(is_verbose(2), 'Removing old lights...', 'Lights removed in {0:.3f}s'):
            root.remove_all('light')
        with timed(is_verbose(2), 'Inserting scene lights...', 'Lights inserted in {0:.3f}s'):
            for light in scene.lights:
                insert_light(root, light)
    # Camera
    if scene.camera:
        with timed(is_verbose(2), 'Removing old cameras...', 'Cameras removed in {0:.3f}s'):
            root.remove_all('camera')
        with timed(is_verbose(2), 'Inserting scene camera...', 'Camera inserted in {0:.3f}s'):
            insert_camera(root, scene.camera)
    # Action
    for i, mesh in enumerate(scene.meshes):
        with timed(is_verbose(2), 'Inserting mesh {}...'.format(i+1), 'Mesh inserted in {0:.3f}s'):
            insert_mesh(root, mesh, *args, **kwargs)

    with timed(is_verbose(1), 'Writing file {}...'.format(filename), 'File written in {0:.3f}s'):
        with open(filename, 'wb') as fp:
            witch = xmlwitch.Builder(version='1.0', encoding='utf-8', stream=fp)
            root.write(witch)


def insert_light(parent, light, default_type='pointlight'):
    light_name = 'Light{}'.format(1 + len(parent.findall('light')))

    light_type = light.type or default_type

    elem = parent.child('light', name=light_name)
    elem.child('type', sval=light_type)
    elem.child('power', fval=str(light.power))
    elem.child('color', **rgba(light.color))

    elem.child('enabled', bval=str(light.enabled).lower())
    elem.child('cast_shadows', bval=str(light.shadows).lower())

    if 'sun' in light_type:
        elem.child('direction', **xyz(light.location))
        elem.child('angle', fval=str(0.5))
        elem.child('samples', ival=str(16))
    else:
        elem.child('from', **xyz(light.location))

    return elem


def insert_camera(parent, camera, default_type='perspective'):
    camera_name = 'cam'  #'Camera{}'.format(1 + len(parent.findall('camera')))

    camera_type = camera.type or default_type

    elem = parent.child('camera', name=camera_name)
    elem.child('type', sval=camera_type)

    elem.child('aperture', fval='0')
    elem.child('bokeh_rotation', fval='0')
    elem.child('bokeh_type', sval='disk1')
    elem.child('dof_distance', fval='0')
    elem.child('focal', fval='1.09375')
    elem.child('from', **xyz(camera.location))
    elem.child('to', **xyz(camera.look_at))
    elem.child('up', **xyz(camera.up_from_look_at))
    elem.child('view_name', sval='')
    elem.child('resx', ival=str(int(camera.resolution[0])))
    elem.child('resy', ival=str(int(camera.resolution[1])))

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

    mesh_id = str(1 + len(parent.findall('mesh')))
    kwargs.update(id=mesh_id)
    top = parent.child('mesh', **kwargs)

    @top.generate
    def generate_mesh():
        for _, vertex in mesh.iter_vertices():
            yield Element('p', **xyz(vertex, mesh.attributes.coordinate_rounding))

        for _, vertex in mesh.iter_texture_vertices():
            yield Element('uv', u=str(vertex[0]), v=str(vertex[1]))

        material = None
        for face in mesh.iter_faces():
            face_material = material_map[face.material] if material_map else face.material
            if face_material and face_material != material:
                yield Element('set_material', sval=str(face_material))
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

            yield Element('f', **kwargs)

    if mesh.attributes.smoothing_degrees is not None:
        parent.child(
            'smooth',
            ID=mesh_id, angle=str(mesh.attributes.smoothing_degrees)
        )

    return top


def insert_ambience(parent, ambience):
    elem = parent.child('integrator', name='default')
    elem.child('AO_color', **rgba(ambience.color))
    elem.child('AO_distance', fval=str(ambience.distance))
    elem.child('AO_samples', ival=str(32))
    elem.child('type', sval='directlighting')
    elem.child('do_AO', bval='true')
    elem.child('bg_transp', bval='false')
    elem.child('bg_transp_refract', bval='false')
    elem.child('caustics', bval='false')
    elem.child('raydepth', ival='2')
    elem.child('shadowDepth', ival='2')
    elem.child('transpShad', bval='false')

    return elem


def insert_background(parent, background):
    elem = parent.find('background')
    if elem:
        elem.remove_all('color')
    else:
        elem = parent.child('background', name='world_background')

        elem.child('ibl', bval='false')
        elem.child('ibl_samples', ival='16')
        elem.child('power', fval='1')
        elem.child('type', sval='constant')

    elem.child('color', **rgba(background))

    return elem


def rgba(color, **kwargs):
    kwargs.update(r=str(color.r), g=str(color.g), b=str(color.b), a=str(color.a))
    return kwargs


def xyz(location, rounding=None, **kwargs):
    if rounding is not None:
        location = tuple(round(c, rounding) for c in location)
    kwargs.update(x=str(location[0]), y=str(location[1]), z=str(location[2]))
    return kwargs
