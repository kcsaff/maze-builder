from .base import BlockIllustratorBase
from maze_builder.random2 import weighted_choice
from maze_builder.emoji import FEATURE_SETS
import random


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
