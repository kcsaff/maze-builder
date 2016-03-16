from .maze import Route, Topology
import random
import itertools

class CastleTwoLevel(object):
    class Room(object):
        def __init__(self, floor, x, y, blocked=False, featured=False):
            self.floor = floor
            self.x, self.y = x, y
            self.blocked = blocked
            self.featured = featured

    class Wall(object):
        def __init__(self, dim, pos, lower_rooms, upper_rooms):
            self.dim = dim
            self.pos = pos
            # self.lower = Route(lower_rooms, conflicts=[id(self)])
            # self.upper = Route(upper_rooms, conflicts=[id(self)])
            # self.route_sets = [[self.lower], [self.upper], [self.lower, self.upper]]

            self.lower = Route(lower_rooms)
            self.upper = Route(upper_rooms)
            self.rooms = set(lower_rooms) | set(upper_rooms)
            self.route_sets = [[self.lower], [self.upper]]

        def name(self, topology):
            if any(room.blocked for room in self.upper.rooms):
                if self.lower in topology:
                    return 'open' + self.dim
                else:
                    return 'wall' + self.dim

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

    def __init__(self, x, y, feature_density=0.01):
        self.x, self.y = x, y
        self.lower_rooms = [[self.Room(0, i, j) for j in range(y)] for i in range(x)]
        self.upper_rooms = [[self.Room(1, i, j) for j in range(y+1)] for i in range(x+1)]

        self.walls = list()
        self.features = list()
        self.topology = Topology()

        # Walls with (lower) varying x
        self.walls.extend(
            self.Wall(
                'y', (i+1, j),
                (self.lower_rooms[i][j], self.lower_rooms[i+1][j]),
                (self.upper_rooms[i+1][j], self.upper_rooms[i+1][j+1]),
            ) for i in range(x-1) for j in range(y)
        )
        # Walls with (lower) varying y
        self.walls.extend(
            self.Wall(
                'x', (i, j+1),
                (self.lower_rooms[i][j], self.lower_rooms[i][j+1]),
                (self.upper_rooms[i][j+1], self.upper_rooms[i+1][j+1]),
            ) for i in range(x) for j in range(y-1)
        )

        for _ in range(int(feature_density*x*y)):
            self._make_feature()

        route_sets = list()
        for wall in self.walls:
            route_sets.extend(wall.route_sets)

        random.shuffle(route_sets)
        for route_set in route_sets:
            self.topology.offer(*route_set)

    def _find_wall(self, rooms):
        rooms = set(rooms)
        for wall in self.walls:
            if rooms.issubset(wall.rooms):
                return wall
        else:
            return None

    def _make_feature(self, retries=0):
        while retries >= 0:
            x = random.randint(1, self.x-1)
            y = random.randint(1, self.y-1)
            lower = (
                self.lower_rooms[x-1][y-1],
                self.lower_rooms[x][y-1],
                self.lower_rooms[x-1][y],
                self.lower_rooms[x][y],
            )

            if any(room.featured for room in lower):
                retries -= 1
                continue
            else:
                break
        else:
            return  # Failed

        for room in lower:
            room.featured = True
        self.upper_rooms[x][y].featured = True

        walls_used = set()
        for rooms in itertools.combinations(lower, 2):
            wall = self._find_wall(rooms)
            if wall and wall not in walls_used:
                self.topology.force(wall.lower)
                walls_used.add(wall)

        self.upper_rooms[x][y].featured = True
        self.features.append(self.upper_rooms[x][y])

    def draw(self, illustrator):
        for wall in self.walls:
            fun = getattr(illustrator, 'draw_' + wall.name(self.topology))
            fun(wall.pos[0] - self.x/2, wall.pos[1] - self.y/2)

        for feature in self.features:
            illustrator.draw_feature(feature.x - self.x/2, feature.y - self.y/2)


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
