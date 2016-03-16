from .faces import V, Surface
import math
import pkgutil


RESOURCE_PACKAGE = 'castles.resources'


def resource(resource_name):
    return pkgutil.get_data(RESOURCE_PACKAGE, resource_name).decode('utf-8')


def template(template_name, **kwargs):
    jinja2.Template(resource(template_name)).render(**kwargs)


class SimpleSurfaceIllustrator(object):
    def __init__(self, wallx, wally=None):
        self.wallx = wallx
        self.wally = wally if wally else wallx.rotate(V.K, degrees=90)

        self.parts = list()

    def draw_wallx(self, x, y, z=0):
        self.parts.append(self.wallx.translate((x, y, z)))

    def draw_wally(self, x, y, z=0):
        self.parts.append(self.wally.translate((x, y, z)))

    def make(self):
        faces = list()
        for part in self.parts:
            faces.extend(part.faces)
        return Surface(faces)


class SimpleTemplateIllustrator(object):
    def __init__(self, template_name='simple.pov.jinja2'):
        self.template_name = template_name

        self.wallx = list()
        self.wally = list()

    def draw_wallx(self, x, y, z=0):
        self.wallx.append((x, y, z))

    def draw_wally(self, x, y, z=0):
        self.wally.append((x, y, z))

    def make(self):
        parts = list()
        parts.append(resource('simple.pov.txt'))
        for wall in self.wallx:
            parts.append('MakeWallX({}, {}, {})'.format(*wall))
        for wall in self.wally:
            parts.append('MakeWallY({}, {}, {})'.format(*wall))
        return '\n'.join(parts)
        #return template(self.template_name, wallx=self.wallx, wally=self.wally)


