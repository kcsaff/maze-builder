from .equivalence import Equivalence
import itertools


class Route(object):
    def __init__(self, rooms, spaces=None, **data):
        self.rooms = rooms
        self.spaces = spaces if spaces is not None else len(rooms)
        self.data = data

    def __repr__(self):
        data = dict(self.data)
        if self.spaces != len(self.rooms):
            data.update(spaces=self.spaces)
        return 'Route({}{})'.format(
            self.rooms,
            ''.join(
                ', {}: {}'.format(*item) for item in sorted(data.items())
            )
        )

    def __lt__(self, other):
        """Only works if rooms support comparison"""
        return self.rooms < other.rooms


class Topology(object):
    def __init__(self, routes=()):
        self.known_routes = set()
        self.known_room_routes = dict()  # Dict from room pairs to routes

        self.active_routes = set()
        self._spaces = dict()

        self.teach(*routes)

    def is_active(self, route):
        route = self._internalize(route)
        return route in self.active_routes

    def teach(self, *routes):
        routes = [self._internalize(route) for route in routes]
        for route in routes:
            if route not in self.known_routes:
                self.known_routes.add(route)
                for rooms in itertools.permutations(route.rooms, 2):
                    room_routes = self.known_room_routes.setdefault(rooms, set())
                    room_routes.add(route)

    def offer(self, *routes):
        routes = [self._internalize(route) for route in routes]
        self.teach(*routes)
        if all(self._check(route) for route in routes):
            return self.force(*routes)
        else:
            return ()

    def force(self, *routes):
        routes = [self._internalize(route) for route in routes]
        self.teach(*routes)
        for route in routes:
            if route not in self.active_routes:
                self.active_routes.add(route)
                self.join(route.rooms)
        return routes

    def routes_connecting(self, rooms):
        for pair in itertools.combinations(rooms, 2):
            if pair in self.known_room_routes:
                yield from self.known_room_routes[pair]

    def any_active_route_connecting(self, rooms):
        for route in self.routes_connecting(rooms):
            if route in self.active_routes:
                return route
        else:
            return None

    # Internal

    def _internalize(self, route):
        if isinstance(route, Route):
            return route
        elif isinstance(route, tuple) and len(route) == 2:
            route_set = self.known_room_routes.get(route)
            if not route_set:
                return Route(route)
            elif len(route_set) == 1:
                return list(route_set)[0]
            else:
                raise RuntimeError(
                    'Cannot internalize room pair into a unique Route: {} available'.format(len(route_set))
                )
        else:
            raise RuntimeError(
                'Cannot internalize route {}'.format(route)
            )

    def space(self, room):
        if room not in self._spaces:
            self._spaces[room] = Equivalence(room)
        return self._spaces[room].canon

    def spaces(self, rooms):
        spaces = list()
        for room in rooms:
            space = self.space(room)
            if space not in spaces:
                spaces.append(space)
        return spaces

    def join(self, rooms):
        if not rooms:
            return
        spaces = list(self.spaces(rooms))
        for space in spaces[1:]:
            spaces[0].join(space)
        return spaces[0].canon

    def _check(self, route):
        return route not in self.active_routes \
               and len(self.spaces(route.rooms)) >= route.spaces
