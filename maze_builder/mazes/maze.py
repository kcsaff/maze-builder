from .equivalence import Equivalence


class Route(object):
    def __init__(self, rooms, conflicts=(), spaces=None, data=None):
        self.rooms = rooms
        self.conflicts = conflicts
        self.spaces = spaces if spaces is not None else len(rooms)
        self.data = data


class Topology(object):
    def __init__(self):
        self.routes = set()
        self._spaces = dict()
        self.conflicts = set()

    def __contains__(self, route):
        return route in self.routes

    def force(self, *routes):
        self.routes.update(routes)
        for route in routes:
            self.join(route.rooms)
            self.conflicts.update(route.conflicts)

    def offer(self, *routes):
        if all(self._check(route) for route in routes):
            self.force(*routes)
            return True
        else:
            return False

    # Internal

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
        #return set(self.space(room) for room in rooms)

    def join(self, rooms):
        if not rooms:
            return
        spaces = list(self.spaces(rooms))
        for space in spaces[1:]:
            spaces[0].join(space)
        return spaces[0].canon

    def _check(self, route):
        return self.conflicts.isdisjoint(route.conflicts) and len(self.spaces(route.rooms)) >= route.spaces
