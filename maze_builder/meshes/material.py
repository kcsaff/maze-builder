from collections import namedtuple
import os.path


class Material(object):
    __slots__ = (
        'path',  # Folder where mtl file was found
        'name',  # Name of material
        'specular_exponent',  # Ns: 0-1000
        'ambient', 'diffuse', 'specular',  # Reflective color triples
        'ior',  # Ni, optical density, index of refraction: 0.001-10
        'dissolve',  # d, 0-1
        'illumination_model',  # an enum
    )

    def __init__(self, path=None, name=None):
        self.path = path
        self.name = name
        self.specular_exponent = 1.0
        self.ambient = Color()
        self.diffuse = Color(1, 1, 1)
        self.specular = Color()
        self.ior = 1.0       # No refraction
        self.dissolve = 1.0  # Solid


class Color(namedtuple('Color', 'r g b')):
    __slots__ = ()

    def __new__(cls, r=0, g=0, b=0):
        return super(cls, Color).__new__(cls, float(r), float(g), float(b))


class Vector(namedtuple('Vector', 'u v w')):
    __slots__ = ()

    def __new__(cls, u=0, v=0, w=0):
        return super(cls, Vector).__new__(cls, float(u), float(v), float(w))


class TextureMap(object):
    __slots__ = (
        'filename',
        'origin',
        'scale'
    )

    def __init__(self, *args):
        self.filename = args[-1]
        self.origin = Vector(0, 0, 0)
        self.scale = Vector(1, 1, 1)

        args = list(args)[:-1]
        end = len(args)
        for i in range(len(args)-1, -1, -1):
            if args[i][0] == '-':
                fun = getattr(self, args[i][1:])
                fun(args[i+1:end])
                end = i

    def o(self, *args):
        args = tuple(args) + (1,) * (3 - len(args))
        self.origin = Vector(*args)

    def s(self, *args):
        args = tuple(args) + (1,) * (3 - len(args))
        self.scale = Vector(*args)


MTL_ATTRS = dict(
    Ns=('specular_exponent', float),
    Ka=('ambient', Color),
    Kd=('diffuse', Color),
    Ks=('specular', Color),
    Ni=('ior', float),
    d=('dissolve', float),
    illum=('illumination_model', int),
)


def read_mtl(filename):
    # http://paulbourke.net/dataformats/mtl/
    path = os.path.dirname(filename)
    materials = dict()
    with open(filename, 'r') as f:
        material = None
        for i, line in enumerate(f):
            def err(s):
                print('{}#{}: {}'.format(filename, i+1, s))

            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts.pop(0)

            if cmd == 'newmtl':
                material = Material(path, *parts)
                materials[material.name] = material
            elif cmd in MTL_ATTRS:
                if not material:
                    err('No material started for command {!r}'.format(cmd))
                attr_name, attr_fun = MTL_ATTRS[cmd]
                attr_value = attr_fun(*parts)
                setattr(material, attr_name, attr_value)
            else:
                err('Unimplemented command {!r}'.format(cmd))

    return materials

