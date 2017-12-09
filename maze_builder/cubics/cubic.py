from maze_builder.mazes.maze import Topology, Route
import random
import math


INF = float('inf')


def _maybe_call(n):
    return n() if callable(n) else n


class Room(object):
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z
        self.exits = set()
        self.entrances = set()
        self.feature = None

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __lt__(self, other):
        return (self.x, self.y, self.z) < (other.x, other.y, other.z)

    def __repr__(self):
        return 'Room({}, {}, {})'.format(self.x, self.y, self.z)

    def coords(self, x=0, y=0, z=0):
        return (self.x + x, self.y + y, self.z + z)

    def coords_along(self, n=1, x=0, y=0, z=0):
        for i in range(n+1):
            yield self.coords(i*x, i*y, i*z)

    def coords_boxing(self, x=1, y=1, z=1):
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    yield self.coords(i, j, k)


class Feature(object):
    def __init__(self, rooms, name=None):
        self.rooms = sorted(rooms)
        for room in self.rooms:
            room.feature = self
        self.name = name
        self.minx = min((room.x for room in self.rooms))
        self.maxx = max((room.x for room in self.rooms))
        self.miny = min((room.y for room in self.rooms))
        self.maxy = max((room.y for room in self.rooms))
        self.minz = min((room.z for room in self.rooms))
        self.maxz = max((room.z for room in self.rooms))


class Cubic(object):
    def __init__(self):
        self.topology = Topology()
        self.rooms = dict()

        self.minx = INF
        self.miny = INF
        self.minz = INF

        self.maxx = -INF
        self.maxy = -INF
        self.maxz = -INF

        self.features = list()

    def center(self):
        return ((self.maxx - self.minx) // 2, (self.maxy - self.miny) // 2, (self.maxy - self.miny) // 2)

    def request_feature(self, width, length=None, height=1, name=None, attempts=20, connected=True):
        length = length or width
        allrooms = list(self.rooms.values())
        print(allrooms)
        for _ in range(attempts):
            r = random.choice(allrooms)
            print((len(allrooms), r))
            rooms = [self.get_room(c, make=False) for c in r.coords_boxing(width, length, height)]
            if not all(rooms):
                continue
            if any(room.feature for room in rooms):
                continue
            if connected:
                self.topology.force(*self.topology.routes_connecting(rooms))
            else:
                self.topology.forget(*self.topology.routes_connecting(rooms))
            feature = Feature(rooms, name)
            self.features.append(feature)
            break
        return self

    def request_chamber(self, width, length=None, height=1, name=None, attempts=20):
        return self.request_feature(width, length, height, name or 'chamber',
                                    attempts=attempts, connected=True)

    def request_barrier(self, width, length=None, height=1, name=None, attempts=20):
        return self.request_feature(width, length, height, name or 'barrier',
                                    attempts=attempts, connected=False)

    def get_room(self, coords, make=True):
        if len(coords) == 2:
            if self.minz < INF:
                coords += (self.minz,)
            else:
                coords += (0,)
        if coords not in self.rooms and make:
            room = Room(*coords)
            self.rooms[coords] = room
            x, y, z = room.x, room.y, room.z

            if x < self.minx:
                self.minx = x
            if x > self.maxx:
                self.maxx = x
            if y < self.miny:
                self.miny = y
            if y > self.maxy:
                self.maxy = y
            if z < self.minz:
                self.minz = z
            if z > self.maxz:
                self.maxz = z

        return self.rooms.get(coords)

    def any_active_route_connecting(self, *coords_list):
        return self.topology.any_active_route_connecting(self.get_room(c, make=False) for c in coords_list)

    def make_route(self, coords_list):
        rooms = [self.get_room(coords) for coords in coords_list]
        if len(rooms) >= 2:
            return Route(rooms)
        else:
            return None

    def offer_route(self, *routes):
        success = False
        for route in self.topology.offer(*routes):
            success = True
            route.rooms[0].exits.add(route)
            route.rooms[-1].entrances.add(route)
        return success

    def prepare(self, x, y, z=1, origin=(0, 0, 0)):
        x, y, z = int(x), int(y), int(z)
        ox, oy, oz = origin
        ox = int(ox) if ox == int(ox) else ox
        oy = int(oy) if oy == int(oy) else oy
        oz = int(oz) if oz == int(oz) else oz

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    self.get_room((ox + i, oy + j, oz + k))

        new_routes = list()

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    if i:
                        new_routes.append(self.make_route(self.get_room((ox + i, oy + j, oz + k)).coords_along(x=-1)))
                    if j:
                        new_routes.append(self.make_route(self.get_room((ox + i, oy + j, oz + k)).coords_along(y=-1)))
                    if k:
                        new_routes.append(self.make_route(self.get_room((ox + i, oy + j, oz + k)).coords_along(z=-1)))
        self.topology.teach(*new_routes)

        return self

    def fill(self):
        routes = list(self.topology.known_room_routes)
        random.shuffle(routes)
        for route in routes:
            self.offer_route(route)

        return self

    def seed(
            self, connection_attempts, origin=(0,0,0),
            x=1, y=None, z=None,
            nx=None, ny=None, nz=None
     ):
        x = x
        y = y if y is not None else x
        z = z if z is not None else x
        nx = nx if nx is not None else x
        ny = ny if ny is not None else y
        nz = nz if nz is not None else z

        def generate_routes(seed):
            routes = [
                self.make_route(seed.coords_along(_maybe_call(x), x=1)),
                self.make_route(seed.coords_along(_maybe_call(y), y=1)),
                self.make_route(seed.coords_along(_maybe_call(z), z=1)),
                self.make_route(seed.coords_along(_maybe_call(nx), x=-1)),
                self.make_route(seed.coords_along(_maybe_call(ny), y=-1)),
                self.make_route(seed.coords_along(_maybe_call(nz), z=-1)),
            ]

            return set(route for route in routes if route)

        seed = self.get_room(origin)
        new_routes = set()

        new_routes.update(generate_routes(seed))
        for _ in range(connection_attempts):
            proposed_route = random.sample(new_routes, 1)[0]
            new_routes.discard(proposed_route)
            if self.offer_route(proposed_route):
                new_routes.update(generate_routes(proposed_route.rooms[-1]))

        return self
