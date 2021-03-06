from maze_builder.mazes.maze import Route, Topology
import random
import itertools


class CastleTwoLevel(object):
    class Room(object):
        def __init__(self, floor, x, y, blocked=False, featured=False):
            self.floor = floor
            self.x, self.y = x, y
            self.blocked = blocked
            self.featured = featured

        def adjacent(self, other):
            return self.floor == other.floor \
                and abs(self.x - other.x) + abs(self.y - other.y) == 1

    class Wall(object):
        def __init__(self, dim, pos, lower_rooms, upper_rooms):
            self.dim = dim
            self.pos = pos

            self.lower = Route(lower_rooms, wall=self)
            self.upper = Route(upper_rooms, wall=self)

            self.rooms = set(lower_rooms) | set(upper_rooms)

        @property
        def routes(self):
            r = list()
            if self.lower and all(not room.blocked for room in self.lower.rooms):
                r.append(self.lower)
            if self.upper and all(not room.blocked for room in self.upper.rooms):
                r.append(self.upper)
            return r

        def name(self, topology):
            if any(room.blocked for room in self.upper.rooms):
                if topology.is_active(self.lower):
                    return 'open' + self.dim
                else:
                    return 'wall' + self.dim

            if topology.is_active(self.upper):
                if topology.is_active(self.lower):
                    return 'arch' + self.dim
                else:
                    return 'wall' + self.dim
            else:
                if topology.is_active(self.lower):
                    return 'open' + self.dim
                else:
                    return 'block' + self.dim

    def __init__(self, x, y, feature_factories=[], verbose=0):
        self.verbose = verbose
        self.x, self.y = x, y
        self.lower_rooms = [[self.Room(0, i, j) for j in range(y)] for i in range(x)]
        self.upper_rooms = [[self.Room(1, i, j) for j in range(y+1)] for i in range(x+1)]

        self.walls = set()
        self.features = list()
        self.topology = Topology()

        if verbose >= 2:
            print('Generating routes...')

        # Walls with (lower) varying x
        self.walls.update(
            self.Wall(
                'y', (i+1, j),
                (self.lower_rooms[i][j], self.lower_rooms[i+1][j]),
                (self.upper_rooms[i+1][j], self.upper_rooms[i+1][j+1]),
            ) for i in range(x-1) for j in range(y)
        )
        # Walls with (lower) varying y
        self.walls.update(
            self.Wall(
                'x', (i, j+1),
                (self.lower_rooms[i][j], self.lower_rooms[i][j+1]),
                (self.upper_rooms[i][j+1], self.upper_rooms[i+1][j+1]),
            ) for i in range(x) for j in range(y-1)
        )

        for wall in self.walls:
            self.topology.teach(*wall.routes)

        if verbose >= 2:
            print('Making features...')
        # Make features, from big to small
        for factory in feature_factories:
            factory.make(self)

        if verbose >= 2:
            print('Filling maze with walls and arches...')

        routes = list()
        for wall in self.walls:
            routes.extend(wall.routes)

        random.shuffle(routes)
        for route in routes:
            self.topology.offer(route)

    def allocate_feature(self, finish, width, length=None, retries=0, upout=False, margin=0, data=None):
        if length is None:
            length = width

        if self.verbose >= 4:
            print('Allocating {}x{} feature...'.format(width, length))

        nupout = 1 if upout else 0
        while retries >= 0:
            x = random.randint(margin, self.x-width-nupout-margin)
            y = random.randint(margin, self.y-length-nupout-margin)
            lower_rooms = [
                self.lower_rooms[x+i][y+j]
                for i in range(width)
                for j in range(length)
            ]
            upper_rooms = [
                self.upper_rooms[x+i][y+j]
                for i in range(1-nupout, width+2*nupout)
                for j in range(1-nupout, length+2*nupout)
            ]
            if any(room.featured for room in lower_rooms + upper_rooms):
                retries -= 1
                continue
            else:
                for room in lower_rooms + upper_rooms:
                    room.featured = True

                finish(self, (x, y), lower_rooms, upper_rooms, data)
                break

    def add_feature(self, feature, x, y, z=0, *data):
        self.features.append((feature, x, y, z, data))

    def force_connect(self, rooms):
        routes = self.topology.routes_connecting(rooms)
        for route in routes:
            self.topology.force(route)
        return routes

    def draw(self, illustrator):
        if self.verbose >= 2:
            print('Drawing {} features...'.format(len(self.features)))

        for feature, x, y, z, data in self.features:
            illustrator.draw_feature(feature, x-self.x/2, y-self.y/2, z, *data)

        if self.verbose >= 2:
            print('Drawing walls...')

        for wall in self.walls:
            fun = getattr(illustrator, 'draw_' + wall.name(self.topology))
            fun(wall.pos[0] - self.x/2, wall.pos[1] - self.y/2)


# TODO: Does this even work anymore?
class CastleOneLevel(object):
    class Room(object):
        def __init__(self, x, y):
            self.x, self.y = x, y

    def __init__(self, x, y):
        self.rooms = [[self.Room(i, j) for j in range(y)] for i in range(x)]
        self.routes = list()
        # Routes with varying x
        self.routes.extend(
            Route((self.rooms[i][j], self.rooms[i+1][j]),
                  data=('wally', 1+i-x/2, j-y/2))
            for i in range(x-1) for j in range(y)
        )
        # Routes with varying y
        self.routes.extend(
            Route((self.rooms[i][j], self.rooms[i][j+1]),
                  data=('wallx', i-x/2, 1+j-y/2))
            for i in range(x) for j in range(y-1)
        )

        self.topology = Topology()
        random.shuffle(self.routes)
        for route in self.routes:
            self.topology.offer(route)

    def draw(self, illustrator):
        for route in self.routes:
            if route not in self.topology:
                item, x, y = route.data
                getattr(illustrator, 'draw_' + item)(x, y)
