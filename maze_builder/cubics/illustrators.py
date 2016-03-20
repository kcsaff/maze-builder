import pkgutil
import jinja2
import random
from maze_builder.emoji import FEATURE_SETS
from maze_builder.random2 import weighted_choice
from PIL import Image
from PIL import ImageColor


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


class BlockIllustratorBase(object):
    def __init__(self, junctions=[1], rooms=[0], xwalls=None, ywalls=None, xhalls=None, yhalls=None, margin=0):
        self.junctions = junctions
        self.rooms = rooms
        self.xwalls = xwalls or junctions
        self.ywalls = ywalls or junctions
        self.xhalls = xhalls or rooms
        self.yhalls = yhalls or rooms
        self.margin = margin

    def draw(self, cubic):
        width = 1 + cubic.maxx - cubic.minx
        height = 1 + cubic.maxy - cubic.miny
        ox = cubic.minx
        oy = cubic.miny
        z = cubic.maxz
        if cubic.maxz != cubic.minz:
            raise RuntimeError('I can only draw 2D images')
        rows = [[None for _ in range(2*width+1)] for _ in range(2*height+1)]

        # Boundaries (left & top)
        for i in range(width):
            rows[0][i*2+1] = weighted_choice(self.xwalls)
        for j in range(height):
            rows[j*2+1][0] = weighted_choice(self.ywalls)

        # Junctions everywhere
        for i in range(width+1):
            for j in range(height+1):
                rows[j*2][i*2] = weighted_choice(self.junctions)

        # Rooms and halls
        for i in range(width):
            x = ox + i
            for j in range(height):
                y = oy + j
                rows[j*2+1][i*2+1] = weighted_choice(self.rooms)

                if cubic.any_active_route_connecting((x, y, z), (x+1, y, z)):
                    rows[j*2+1][i*2+2] = weighted_choice(self.xhalls)
                else:
                    rows[j*2+1][i*2+2] = weighted_choice(self.ywalls)

                if cubic.any_active_route_connecting((x, y, z), (x, y+1, z)):
                    rows[j*2+2][i*2+1] = weighted_choice(self.yhalls)
                else:
                    rows[j*2+2][i*2+1] = weighted_choice(self.xwalls)

        if self.margin:
            return [line[self.margin:-self.margin] for line in rows[self.margin:-self.margin]]
        else:
            return rows


class ImageBlockIllustrator(BlockIllustratorBase):
    def __init__(self, wall_colors=[(0,0,0)], hall_colors=[(255,255,255)]):
        super().__init__(wall_colors, hall_colors)

    def draw(self, cubic):
        data = super().draw(cubic)
        image = Image.new('RGB', (len(data[0]), len(data)))
        image.putdata(sum(data, []))
        return image


class UnicodeFullBlockIllustrator(BlockIllustratorBase):
    WIDE_SPACE = '\u3000'
    THIN_SPACE = ' '
    SPACES = THIN_SPACE
    BLOCKS = '█'

    def __init__(self, blocks=None, spaces=None, newline='\n', charsep='', margin=2):
        super().__init__(
            junctions=blocks or self.BLOCKS,
            rooms=spaces or self.SPACES,
            margin=margin
        )

    def draw(self, cubic):
        return self.newline.join(
            self.charsep.join(line)
            for line in super().draw(cubic)
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


