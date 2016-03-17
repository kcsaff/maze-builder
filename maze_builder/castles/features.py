import random
from maze_builder.mazes.maze import Route


class FeatureFactory(object):
    def _count(self, castle):
        return int(castle.x*castle.y*self.density)


class Courtyards(FeatureFactory):
    def __init__(self, density, widthfun=lambda: random.randint(2, 5), lengthfun=None):
        self.density = density
        self.widthfun = widthfun
        self.lengthfun = lengthfun or widthfun

    def make(self, castle, count=None):
        count = count or self._count(castle)
        if castle.verbose >= 3:
            print('Generating <={} courtyards...'.format(count))

        for _ in range(count):
            width, length = self.widthfun(), self.lengthfun()
            castle.allocate_feature(self.finish, width, length, retries=2, data=(width, length))

    def finish(self, castle, pos, lower, upper, data):
        width, length = data

        castle._force_lower_connect(lower)

        for room in upper:
            room.blocked = True

        castle.features.append((self, (pos[0], pos[1], width, length or width)))

        if castle.verbose >= 4:
            print('Placed {}x{} courtyard at {}, {}'.format(width, length or width, pos[0], pos[1]))

    def draw(self, castle, data, illustrator):
        illustrator.draw_courtyard(data[0] - castle.x/2, data[1] - castle.y/2, data[2], data[3])


class Stairs(FeatureFactory):
    def __init__(self, density):
        self.density = density

    def make(self, castle, count=None):
        count = count or self._count(castle)
        if castle.verbose >= 3:
            print('Generating <={} stairs...'.format(count))

        for _ in range(count):
            dims, uprel, dir = random.choice((
                # Dimensions, relative of upper room, direction
                [(2, 1), (1, 1), (0, 1)],
                [(1, 2), (1, 1), (1, 0)],
                [(2, 1), (1, 0), (0, -1)],
                [(1, 2), (0, 1), (-1, 0)]
            ))
            castle.allocate_feature(self.finish, *dims, retries=2, margin=1, data=(dims, uprel, dir))

    def finish(self, castle, pos, lower, upper, data):
        dims, uprel, dir = data
        for wall in castle._force_lower_connect(lower):
            castle.walls.remove(wall)

        upper = castle.upper_rooms[lower[0].x + uprel[0]][lower[0].y + uprel[1]]
        castle.topology.force(Route([upper] + lower))

        center = (lower[0].x + lower[1].x + 1) / 2, (lower[0].y + lower[1].y + 1) / 2

        if castle.verbose >= 4:
            print('Placed {}x{} stair at {}, {}'.format(dims[0], dims[1], pos[0], pos[1]))

        castle.features.append((self, (center[0], center[1], dir[0], dir[1])))

    def draw(self, castle, data, illustrator):
        illustrator.draw_stair(data[0] - castle.x/2, data[1] - castle.y/2, data[2], data[3])


class Towers(FeatureFactory):
    def __init__(self, density, widthfun=lambda: random.randint(1, 3), lengthfun=lambda: random.randint(1, 3)):
        self.density = density
        self.widthfun = widthfun
        self.lengthfun = lengthfun

    def make(self, castle, count=None):
        count = count or self._count(castle)
        if castle.verbose >= 3:
            print('Generating <={} towers...'.format(count))

        for _ in range(count):
            width, length = self.widthfun(), self.lengthfun()
            castle.allocate_feature(self.finish, width, length, retries=2, upout=True, data=(width, length))

    def finish(self, castle, pos, lower, upper, data):
        width, length = data

        for room in lower + upper:
            room.blocked = True

        castle.features.append((self, (pos[0], pos[1], width, length or width)))

        if castle.verbose >= 4:
            print('Placed {}x{} tower at {}, {}'.format(width, length or width, pos[0], pos[1]))

    def draw(self, castle, data, illustrator):
        illustrator.draw_tower(data[0] - castle.x/2, data[1] - castle.y/2, data[2], data[3])


class Spires(FeatureFactory):
    def __init__(self, density):
        self.density = density

    def make(self, castle, count=None):
        count = count or self._count(castle)
        if castle.verbose >= 3:
            print('Generating <={} spires...'.format(count))

        for _ in range(count):
            castle.allocate_feature(self.finish, 2, 2, retries=1)

    def finish(self, castle, pos, lower, upper, data=None):
        walls_used = set()
        for rooms in castle._adjacent_rooms(lower):
            for wall in castle._find_walls(rooms):
                if wall not in walls_used:
                    castle.topology.force(wall.lower)
                    walls_used.add(wall)

        castle.features.append((self, (pos[0] + 1, pos[1] + 1)))

        if castle.verbose >= 4:
            print('Placed {}x{} spire at {}, {}'.format(2, 2, pos[0], pos[1]))

    def draw(self, castle, data, illustrator):
        illustrator.draw_spire(data[0] - castle.x/2, data[1] - castle.y/2)
