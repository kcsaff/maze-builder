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

        self.walls = list()
        self.features = list()

        self.feature_map = dict(
            spire='MakeSpire',
            courtyard='MakeCourtyard',
            tower='MakeTower',
            stair='MakeStair',
        )

    def reset(self):
        self.walls = list()
        self.features = list()

    def draw_wallx(self, x, y, z=0):
        self.walls.append(('MakeWallX', (x, y, z)))

    def draw_wally(self, x, y, z=0):
        self.walls.append(('MakeWallY', (x, y, z)))

    def draw_archx(self, x, y, z=0):
        self.walls.append(('MakeArchX', (x, y, z)))

    def draw_archy(self, x, y, z=0):
        self.walls.append(('MakeArchY', (x, y, z)))

    def draw_openx(self, x, y, z=0):
        self.walls.append(('MakeOpenX', (x, y, z)))

    def draw_openy(self, x, y, z=0):
        self.walls.append(('MakeOpenY', (x, y, z)))

    def draw_blockx(self, x, y, z=0):
        self.walls.append(('MakeBlockX', (x, y, z)))

    def draw_blocky(self, x, y, z=0):
        self.walls.append(('MakeBlockY', (x, y, z)))

    def draw_feature(self, feature, x, y, z=0, *data):
        self.features.append((self.feature_map[feature], (x, y, z), data))

    def _choose_template_name(self):
        return weighted_choice(*zip(*self.weighted_template_dict.items()))

    def make(self):
        return template(
            self._choose_template_name(),
            walls=self.walls,
            features=self.features,
            seed=random.randint(1, 9999)
        )
