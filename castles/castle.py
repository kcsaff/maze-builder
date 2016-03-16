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

        def adjacent(self, other):
            return self.floor == other.floor \
                and abs(self.x - other.x) + abs(self.y - other.y) == 1

    class Wall(object):
        def __init__(self, dim, pos, lower_rooms, upper_rooms):
            self.dim = dim
            self.pos = pos

            self.lower = Route(lower_rooms)
            self.upper = Route(upper_rooms)
            self.rooms = set(lower_rooms) | set(upper_rooms)

        @property
        def route_sets(self):
            r = list()
            if all(not room.blocked for room in self.lower.rooms):
                r.append([self.lower])
            if all(not room.blocked for room in self.upper.rooms):
                r.append([self.upper])
            return r

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

    def __init__(self, x, y, spire_density=0.01, courtyard_density=0.01, tower_density=0.01):
        self.x, self.y = x, y
        self.lower_rooms = [[self.Room(0, i, j) for j in range(y)] for i in range(x)]
        self.upper_rooms = [[self.Room(1, i, j) for j in range(y+1)] for i in range(x+1)]

        self.walls = list()
        self.spires = list()
        self.towers = list()
        self.courtyards = list()
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

        for _ in range(int(spire_density*x*y)):
            self._make_spire()

        for _ in range(int(courtyard_density*x*y)):
            self._make_courtyard(random.randint(2, 5))

        for _ in range(int(tower_density*x*y)):
            self._make_tower(random.randint(1, 3), random.randint(1, 3))

        route_sets = list()
        for wall in self.walls:
            route_sets.extend(wall.route_sets)

        random.shuffle(route_sets)
        for route_set in route_sets:
            self.topology.offer(*route_set)

    def _find_walls(self, rooms):
        rooms = set(rooms)
        for wall in self.walls:
            if rooms.issubset(wall.rooms):
                yield wall

    def _alloc_feature(self, width, length=None, retries=0, upout=False):
        if length is None:
            length = width
        nupout = 1 if upout else 0
        while retries >= 0:
            x = random.randint(0, self.x-width-nupout)
            y = random.randint(0, self.y-length-nupout)
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
                break
        else:
            return None, None, None
        for room in lower_rooms + upper_rooms:
            room.featured = True
        return (x, y), lower_rooms, upper_rooms

    def _make_courtyard(self, width, length=None, retries=2):
        pos, lower, upper = self._alloc_feature(width, length, retries)
        if pos is None:
            return

        walls_used = set()
        for rooms in self._adjacent_rooms(lower):
            for wall in self._find_walls(rooms):
                if wall not in walls_used:
                    self.topology.force(wall.lower)
                    walls_used.add(wall)

        for room in upper:
            room.blocked = True

        self.courtyards.append((pos[0], pos[1], width, length or width))

    def _make_tower(self, width, length=None, retries=2):
        pos, lower, upper = self._alloc_feature(width, length, retries, upout=True)
        if pos is None:
            return

        for room in lower + upper:
            room.blocked = True

        self.towers.append((pos[0], pos[1], width, length or width))

    def _adjacent_rooms(self, rooms):
        for room0, room1 in itertools.combinations(rooms, 2):
            if room0.adjacent(room1):
                yield room0, room1

    def _make_spire(self, retries=0):
        pos, lower, upper = self._alloc_feature(2, 2, retries)
        if pos is None:
            return

        walls_used = set()
        for rooms in self._adjacent_rooms(lower):
            for wall in self._find_walls(rooms):
                if wall not in walls_used:
                    self.topology.force(wall.lower)
                    walls_used.add(wall)

        self.spires.append((pos[0] + 1, pos[1] + 1))

    def draw(self, illustrator):
        for wall in self.walls:
            fun = getattr(illustrator, 'draw_' + wall.name(self.topology))
            fun(wall.pos[0] - self.x/2, wall.pos[1] - self.y/2)

        for spire in self.spires:
            illustrator.draw_spire(spire[0] - self.x/2, spire[1] - self.y/2)

        for courtyard in self.courtyards:
            illustrator.draw_courtyard(courtyard[0] - self.x/2, courtyard[1] - self.y/2, courtyard[2], courtyard[3])

        for tower in self.towers:
            illustrator.draw_tower(tower[0] - self.x/2, tower[1] - self.y/2, tower[2], tower[3])


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
