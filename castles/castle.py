from .maze import Route, Topology
import random


class CastleTwoLevel(object):
    class Room(object):
        def __init__(self, floor, x, y):
            self.floor = floor
            self.x, self.y = x, y

        def pos(self):
            return self.x, self.y

    class Wall(object):
        def __init__(self, dim, lower_rooms, upper_rooms):
            self.dim = dim
            # self.lower = Route(lower_rooms, conflicts=[id(self)])
            # self.upper = Route(upper_rooms, conflicts=[id(self)])
            # self.route_sets = [[self.lower], [self.upper], [self.lower, self.upper]]

            self.lower = Route(lower_rooms)
            self.upper = Route(upper_rooms)
            self.route_sets = [[self.lower], [self.upper]]

        def name(self, topology):
            if self.upper in topology:
                if self.lower in topology:
                    return 'arch' + self.dim
                else:
                    return 'wall' + self.dim
            else:
                if self.lower in topology:
                    return 'open' + self.dim
                else:
                    return 'block' + self.dim

        def pos(self):
            return self.lower.rooms[0].pos()

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.lower_rooms = [[self.Room(0, i, j) for j in range(y)] for i in range(x)]
        self.upper_rooms = [[self.Room(1, i, j) for j in range(y+1)] for i in range(x+1)]

        self.walls = list()

        # Walls with (lower) varying x
        self.walls.extend(
            self.Wall(
                'y',
                (self.lower_rooms[i][j], self.lower_rooms[i+1][j]),
                (self.upper_rooms[i+1][j], self.upper_rooms[i+1][j+1]),
            ) for i in range(x-1) for j in range(y)
        )
        # Walls with (lower) varying y
        self.walls.extend(
            self.Wall(
                'x',
                (self.lower_rooms[i][j], self.lower_rooms[i][j+1]),
                (self.upper_rooms[i][j+1], self.upper_rooms[i+1][j+1]),
            ) for i in range(x) for j in range(y-1)
        )

        route_sets = list()
        for wall in self.walls:
            route_sets.extend(wall.route_sets)

        self.topology = Topology()
        random.shuffle(route_sets)
        for route_set in route_sets:
            self.topology.offer(*route_set)

    def draw(self, illustrator):
        misses = 0
        for wall in self.walls:
            fun = getattr(illustrator, 'draw_' + wall.name(self.topology))
            fun(wall.pos()[0] - self.x/2, wall.pos()[1] - self.y/2)


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
