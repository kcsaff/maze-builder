class Color(object):
    __slots__ = tuple('rgba')

    def __init__(self, r=0, g=0, b=0, a=1):
        self.r, self.g, self.b, self.a = r, g, b, a

    @classmethod
    def hex(cls, value, a=1):
        r = ((value >> 32) & 0xFF) / 255.0
        g = ((value >> 16) & 0xFF) / 255.0
        b = ((value >>  0) & 0xFF) / 255.0
        return cls(r, g, b, a)

    def components(self, scale=1, norm=float):
        return norm(scale*self.r), norm(scale*self.g), norm(scale*self.b), norm(scale*self.a)

    def blowout(self, value=1):
        mult = min(value / c for c in self.components()[:3] if c > 0)
        return Color(self.r*mult, self.g*mult, self.b*mult,self.a)

    def __mul__(self, scalar):
        return Color(self.r*scalar, self.g*scalar, self.b*scalar, self.a)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __add__(self, other):
        return Color(self.r+other.r, self.g+other.g, self.b+other.b, (self.a+other.a)/2)

    def __sub__(self, other):
        return Color(self.r-other.r, self.g-other.g, self.b-other.b, (self.a+other.a)/2)


Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(1, 1, 1)
Color.SKY_BLUE = Color.hex(0x87CEEB)
Color.LIGHT_SKY_BLUE = Color.hex(0x87CEFA)
Color.DEEP_SKY_BLUE = Color.hex(0x00BFFF)


class Camera(object):
    def __init__(
        self,
        location=(10, 10, 10), look_at=(0, 0, 0), up=(0, 0, 1),
        resolution=(960, 540), type=None
    ):
        """up is RELATIVE"""
        self.resolution = resolution
        self.location = location
        self.look_at = look_at
        self.up = up
        self.type = type

    @property
    def up_from_look_at(self):
        return tuple(c0+c1 for c0,c1 in zip(self.look_at, self.up))


class Light(object):
    def __init__(self, location=(10, 10, 10), color=Color.WHITE, power=1.0, type=None):
        self.enabled = True
        self.shadows = True

        self.location = location
        self.color = color
        self.power = power
        self.type = type


class Ambience(object):
    def __init__(self, color=Color.WHITE, distance=1):
        self.color = color
        self.distance = distance


class Scene(object):
    def __init__(self):
        self.lights = list()
        self.camera = None
        self.materials = dict()
        self.meshes = list()
        self.background = None
        self.ambience = None

    def add_mesh(self, *meshes):
        self.meshes.extend(meshes)
        return self

    def add_light(self, *lights):
        self.lights.extend(lights)
        return self

    def set_camera(self, camera):
        self.camera = camera
        return self

    def set_background(self, background):
        self.background = background
        return self

    def set_ambience(self, ambience):
        self.ambience = ambience
        return self
