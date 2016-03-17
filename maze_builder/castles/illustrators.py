import pkgutil
import jinja2
import random
from maze_builder.random2 import weighted_choice


RESOURCE_PACKAGE = 'maze_builder.castles.resources'


def resource(resource_name):
    return pkgutil.get_data(RESOURCE_PACKAGE, resource_name).decode('utf-8')


def template(template_name, **kwargs):
    return jinja2.Template(resource(template_name)).render(**kwargs)


class WeightedTemplateIllustrator(object):
    def __init__(self, weighted_template_dict):
        self.weighted_template_dict = weighted_template_dict

        self.parts = list()
        self.blocks = list()

    def reset(self):
        self.parts = list()
        self.blocks = list()

    def draw_wallx(self, x, y, z=0):
        self.parts.append(('MakeWallX', (x, y, z)))

    def draw_wally(self, x, y, z=0):
        self.parts.append(('MakeWallY', (x, y, z)))

    def draw_archx(self, x, y, z=0):
        self.parts.append(('MakeArchX', (x, y, z)))

    def draw_archy(self, x, y, z=0):
        self.parts.append(('MakeArchY', (x, y, z)))

    def draw_openx(self, x, y, z=0):
        self.parts.append(('MakeOpenX', (x, y, z)))

    def draw_openy(self, x, y, z=0):
        self.parts.append(('MakeOpenY', (x, y, z)))

    def draw_blockx(self, x, y, z=0):
        self.parts.append(('MakeBlockX', (x, y, z)))

    def draw_blocky(self, x, y, z=0):
        self.parts.append(('MakeBlockY', (x, y, z)))

    def draw_spire(self, x, y, z=0):
        self.parts.append(('MakeSpire', (x, y, z)))

    def draw_courtyard(self, x, y, width, length):
        self.blocks.append(('MakeCourtyard', (x, y, 0), (width, length)))

    def draw_tower(self, x, y, width, length):
        self.blocks.append(('MakeTower', (x, y, 0), (width, length)))

    def draw_stair(self, x, y, dx, dy):
        self.blocks.append(('MakeStair', (x, y, 0), (dx, dy)))

    def _choose_template_name(self):
        return weighted_choice(*zip(*self.weighted_template_dict.items()))

    def make(self):
        return template(
            self._choose_template_name(),
            parts=self.parts,
            blocks=self.blocks,
            seed=random.randint(1, 9999)
        )
