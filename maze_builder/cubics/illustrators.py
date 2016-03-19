import pkgutil
import jinja2
import random
import string
from maze_builder.random2 import weighted_choice


RESOURCE_PACKAGE = 'maze_builder.satellites.resources'


def resource(resource_name):
    return pkgutil.get_data(RESOURCE_PACKAGE, resource_name).decode('utf-8')


def template(template_name, **kwargs):
    return jinja2.Template(resource(template_name)).render(**kwargs)


class TemplateIllustrator(object):
    def __init__(self, template='satellite.pov.jinja2'):
        self.template = template

    def draw(self, cubic):
        return template(
            self.template,
            connections=cubic.topology.active_routes,
        )


HAPPY_FACES = ''.join(
    [chr(x) for x in range(0x1f600, 0x1f608)]
    + [chr(x) for x in range(0x1f609, 0x1f60c)]
    + ['\U0001f60e\u263a\U0001f642\U0001f917\U0001f913\U0001f60c\U0001f61b\U0001f61c\U0001f61d\U0001f643']
    + ['\U0001f911']
)

LOVE_FACES = ''.join(
    ['\U0001f60d\U0001f633']
    + [chr(x) for x in range(0x1f617, 0x1f61b)]
)

NEUTRAL_FACES = ''.join(
    ['\U0001f914\U0001f610\U0001f611\U0001f636\U0001f644\U0001f60f\U0001f62a\U0001f634\U0001f612\U0001f614']
)

SAD_FACES = ''.join(
    ['\U0001f623\u2639\U0001f641\U0001f616\U0001f61e\U0001f622\U0001f62d\U0001f629']
)

SCARED_FACES = ''.join(
    ['\U0001f62e\U0001f910\U0001f625\U0001f62f\U0001f62b\U0001f613\U0001f615\U0001f632\U0001f61f\U0001f627\U0001f628']
    + ['\U0001f630\U0001f631\U0001f635']
)

SICK_FACES = ''.join(
    ['\U0001f637\U0001f912\U0001f915']
)

ANGRY_FACES = ''.join(
    ['\U0001f624\U0001f62c\U0001f621\U0001f620']
)

MONSTER_FACES = ''.join(
    ['\U0001f608\U0001f47f\U0001f479\U0001f47a']
)

DEAD_THINGS = ''.join(
    ['\U0001f480\u2620\U0001f47b']
)

SCIFI_FACES = ''.join(
    ['\U0001f47d\U0001f47e\U0001f916']
)

FEATURE_SETS = {
    string.ascii_uppercase: 100,
    string.digits: 100,
    NEUTRAL_FACES: 100,
    SCARED_FACES: 100,
}


class UnicodeQuarterBlockIllustrator(object):
    WIDE_SPACE = '\u3000'
    THIN_SPACE = ' '
    BLOCKS = ''.join([
             '▖', '▗', '▄',
        '▝', '▞', '▐', '▟',
        '▘', '▌', '▚', '▙',
        '▀', '▛', '▜', '█',
    ])
    BLOCKS = ''.join(['▛', '▀', '▌', '▘'])

    def __init__(self, blocks=None, newline='\n', charsep='', feature_sets=None):
        self.blocks = blocks or self.BLOCKS
        self.charsep = charsep
        self.newline = newline
        self.feature_sets = feature_sets or FEATURE_SETS

    def draw(self, cubic):
        width = 1 + cubic.maxx - cubic.minx
        height = 1 + cubic.maxy - cubic.miny
        ox = cubic.minx
        oy = cubic.miny
        z = cubic.maxz
        if cubic.maxz != cubic.minz:
            raise RuntimeError('I can only draw 2D images')
        lines = [[self.blocks[0]] * (width+1) for _ in range(height+1)]

        for j in range(0, height+1):
            y = oy + j
            for i in range(0, width+1):
                x = ox + i

                val = 0
                if i >= width or cubic.any_active_route_connecting((x, y-1, z), (x, y, z)):
                    val += 2
                if j >= height or cubic.any_active_route_connecting((x-1, y, z), (x, y, z)):
                    val += 1

                lines[j][i] = self.blocks[val]

        feature_set = weighted_choice(self.feature_sets)

        size1_features = [feature for feature in cubic.features if len(feature.rooms) == 1]
        feature_symbols = random.sample(feature_set, len(size1_features))
        for feature, symbol in zip(size1_features, feature_symbols):
            lines[feature.rooms[0].y][feature.rooms[0].x] = symbol

        return self.newline.join(self.charsep.join(line) for line in lines)


class UnicodeFullBlockIllustrator(object):
    WIDE_SPACE = '\u3000'
    THIN_SPACE = ' '
    BLOCKS = ''.join([
             '▖', '▗', '▄',
        '▝', '▞', '▐', '▟',
        '▘', '▌', '▚', '▙',
        '▀', '▛', '▜', '█',
    ])
    SPACES = THIN_SPACE
    BLOCKS = '█'

    def __init__(self, blocks=None, spaces=None, newline='\n', charsep='', feature_sets=None, margin=2):
        self.blocks = blocks or self.BLOCKS
        self.spaces = spaces or self.SPACES
        self.charsep = charsep
        self.newline = newline
        self.feature_sets = feature_sets or FEATURE_SETS
        self.margin = margin

    def draw(self, cubic):
        width = 1 + cubic.maxx - cubic.minx
        height = 1 + cubic.maxy - cubic.miny
        ox = cubic.minx
        oy = cubic.miny
        z = cubic.maxz
        if cubic.maxz != cubic.minz:
            raise RuntimeError('I can only draw 2D images')
        lines = [[weighted_choice(self.blocks) for _ in range(2*width+1)] for _ in range(2*height+1)]

        for i in range(width):
            x = ox + i
            for j in range(height):
                y = oy + j
                lines[j*2+1][i*2+1] = weighted_choice(self.spaces)
                if cubic.any_active_route_connecting((x, y, z), (x, y+1, z)):
                    lines[j*2+2][i*2+1] = weighted_choice(self.spaces)
                if cubic.any_active_route_connecting((x, y, z), (x+1, y, z)):
                    lines[j*2+1][i*2+2] = weighted_choice(self.spaces)

        return self.newline.join(
            self.charsep.join(line[self.margin:-self.margin])
            for line in lines[self.margin:-self.margin]
        )


class UnicodeWallIllustrator(object):
    WIDE_SPACE = '\u3000'
    THIN_SPACE = ' '
    THICK_WALLS = '╺╹┗╸━┛┻╻┏┃┣┓┳┫╋'

    def __init__(self, walls=None, newline='\n', charsep=''):
        self.walls = walls or self.THIN_SPACE + self.THICK_WALLS
        self.charsep = charsep
        self.newline = newline

    def draw(self, cubic):
        width = 1 + cubic.maxx - cubic.minx
        height = 1 + cubic.maxy - cubic.miny
        ox = cubic.minx
        oy = cubic.miny
        z = cubic.maxz
        if cubic.maxz != cubic.minz:
            raise RuntimeError('I can only draw 2D images')
        lines = [[self.walls[0]] * (width+1) for _ in range(height+1)]

        for j in range(0, height+1):
            y = oy + j
            for i in range(0, width+1):
                x = ox + i

                val = 0
                if i < width and not cubic.any_active_route_connecting((x, y-1, z), (x, y, z)):
                    val += 1
                if j < height and not cubic.any_active_route_connecting((x-1, y, z), (x, y, z)):
                    val += 2
                if i > 0 and not cubic.any_active_route_connecting((x-1, y-1, z), (x-1, y, z)):
                    val += 4
                if j > 0 and not cubic.any_active_route_connecting((x-1, y-1, z), (x, y-1, z)):
                    val += 8

                lines[j][i] = self.walls[val]

        print(self.margin)
        return self.newline.join(
            self.charsep.join(line)
            for line in lines
        )


