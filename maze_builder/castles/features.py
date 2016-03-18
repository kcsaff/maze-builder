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

        castle.force_connect(lower)

        for room in upper:
            room.blocked = True

        castle.add_feature('courtyard', pos[0], pos[1], 0, width, length or width)

        if castle.verbose >= 4:
            print('Placed {}x{} courtyard at {}, {}'.format(width, length or width, pos[0], pos[1]))


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
        for route in castle.force_connect(lower):
            if 'wall' in route.data:
                castle.walls.discard(route.data['wall'])

        upper = castle.upper_rooms[lower[0].x + uprel[0]][lower[0].y + uprel[1]]
        castle.topology.force(Route([upper] + lower))

        center = (lower[0].x + lower[1].x + 1) / 2, (lower[0].y + lower[1].y + 1) / 2

        if castle.verbose >= 4:
            print('Placed {}x{} stair at {}, {}'.format(dims[0], dims[1], pos[0], pos[1]))

        castle.add_feature('stair', center[0], center[1], 0, dir[0], dir[1])


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

        castle.add_feature('tower', pos[0], pos[1], 0, width, length or width)

        if castle.verbose >= 4:
            print('Placed {}x{} tower at {}, {}'.format(width, length or width, pos[0], pos[1]))


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
        castle.force_connect(lower)

        castle.add_feature('spire', pos[0] + 1, pos[1] + 1, 0)

        if castle.verbose >= 4:
            print('Placed {}x{} spire at {}, {}'.format(2, 2, pos[0], pos[1]))
