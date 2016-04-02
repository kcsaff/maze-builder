from collections import namedtuple
import math
import itertools


inf = float('inf')


def area(polygon, signed=False):
    L = len(polygon)
    a = 0.5 * sum(
        p[0] * q[1] - q[0] * p[1]
        for p, q in edges(polygon)
    )
    if not signed:
        a = abs(a)
    return a


def centroid(polygon):
    m = 1 / 6 / area(polygon, signed=True)
    L = len(polygon)
    cx = m * sum(
        (p[0] + q[0]) *
        (p[0] * q[1] - q[0] * p[1]) for p, q in edges(polygon)
    )
    cy = m * sum(
        (p[1] + q[1]) *
        (p[0] * q[1] - q[0] * p[1]) for p, q in edges(polygon)
    )
    return cx, cy


def edges(polygon):
    s = len(polygon)
    return ((polygon[i], polygon[(i+1) % s]) for i in range(s))


def winding_number(polygon, point):
    """
    http://geomalgorithms.com/a03-_inclusion.html
    """
    result = 0
    for p, q in edges(polygon):
        if p[1] <= point[1]:
            if q[1] > point[1] and _is_left(p, q, point) > 0:
                result += 1
        else:
            if q[1] <= point[1] and _is_left(p, q, point) < 0:
                result -= 1
    return result


def contains(polygon, point):
    return winding_number(polygon, point) != 0


def limits(polygon, axis):
    vals = [sum(v * a for v, a in zip(axis, vertex)) for vertex in polygon]
    return min(vals), max(vals)


def _is_left(p0, p1, p2):
    """
    Input:  three points P0, P1, and P2
    Return: >0 for P2 left of the line through P0 and P1
            =0 for P2  on the line
            <0 for P2  right of the line
    See: http://geomalgorithms.com/a01-_area.html
    """
    return ((p1[0] - p0[0]) * (p2[1] - p0[1]) -
            (p2[0] - p0[0]) * (p1[1] - p0[1])
            )


class BoundingBox(object):
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def __repr__(self):
        return 'BoundingBox({}, {})'.format(self.p0, self.p1)

    @classmethod
    def around(cls, *polygons):
        if len(polygons) == 1 and hasattr(polygons[0], 'bbox') and polygons[0].bbox:
            return polygons[0].bbox
        p0 = tuple(min(c) for c in zip(*itertools.chain(*polygons)))
        p1 = tuple(max(c) for c in zip(*itertools.chain(*polygons)))
        return cls(p0, p1)

    def vertices(self):
        for index in range(1 << self.dim()):
            yield tuple(
                m1 if (1 & (index >> i)) else m0
                for m0, m1, i
                in zip(self.p0, self.p1, range(self.dim()))
            )

    def contains(self, point, inclusive=True):
        if inclusive:
            return all(c0 <= cp <= c1 for c0, cp, c1 in zip(self.p0, point, self.p1))
        else:
            return all(c0 < cp < c1 for c0, cp, c1 in zip(self.p0, point, self.p1))

    def collides(self, polygon, approximate=False):
        if approximate and not isinstance(polygon, BoundingBox):
            polygon = BoundingBox.around(polygon)
        if isinstance(polygon, BoundingBox):
            return self._collides_bounding_box(polygon)
        else:
            return any(self.contains(vertex) for vertex in polygon) \
                or polygon.contains(self.center) \
                or any(self._clip_segment(*edge) for edge in edges(polygon)) \
                or False

                # or any(polygon.contains(vertex) for vertex in self.vertices()) \

    @property
    def center(self):
        return tuple((c0 + c1) / 2 for c0, c1 in zip(self.p0, self.p1))

    def dim(self):
        return len(self.p0)

    def split(self, center=None):
        center = center or self.center
        return [self._split_quadrant(i, center=center) for i in range(1 << self.dim())]

    def quadrant(self, point, center=None):
        center = center or self.center
        return sum(1 << i if point[i] >= center[i] else 0 for i in range(self.dim()))

    def _cmp(self, point):
        return tuple(-1 if p < m0 else 0 if p <= m1 else 1 for p, m0, m1 in zip(point, self.p0, self.p1))

    def _collides_bounding_box(self, bbox):
        return not all(0 < (m0 - o1) * (m1 - o0) for m0, m1, o0, o1 in zip(self.p0, self.p1, bbox.p0, bbox.p1))

    def _clip_segment(self, v0, v1):
        z = zip(self.p0, self.p1, v0, v1)
        if any(o0 < m0 > o1 or o0 > m1 < o1 for m0, m1, o0, o1 in z):
            return None
        orders = [
            (m0, m1, o0, o1 - o0) if o1 > o0 else (m1, m0, o0, o1 - o0)
            for m0, m1, o0, o1 in zip(self.p0, self.p1, v0, v1)
            if o0 != o1
        ]
        minarg = max(0, max(((m0 - o0) / od for m0,_,o0,od in orders), default=0))
        maxarg = min(1, min(((m1 - o0) / od for _,m1,o0,od in orders), default=1))

        # print((self.p0, self.p1, v0, v1, minarg, maxarg))

        if minarg < maxarg:
            r0 = tuple(o0 + minarg * od for _,_,o0,od in orders)
            r1 = tuple(o0 + maxarg * od for _,_,o0,od in orders)
            return r0, r1
        else:
            return None

    def _split_quadrant(self, index, center=None):
        if isinstance(index, int):
            indices = [(index >> i) & 1 for i in range(self.dim())]
        else:
            indices = index
        center = center or self.center
        low = list()
        high = list()
        for i, c0, cc, c1 in zip(indices, self.p0, center, self.p1):
            if i > 0:
                low.append(cc)
                high.append(c1)
            else:
                low.append(c0)
                high.append(cc)
        return BoundingBox(tuple(low), tuple(high))


class Polygon(object):
    def __init__(self, vertices, indices=None):
        self.vertices = vertices
        self.indices = indices or range(len(vertices))
        self.bbox = None
        self._centroid = None

    def __len__(self):
        return len(self.indices)

    def __iter__(self):
        return (self.vertices[i] for i in self.indices)

    def __getitem__(self, item):
        return self.vertices[self.indices[item % len(self.indices)]]

    def __repr__(self):
        return 'Polygon({})'.format(', '.join(str(v) for v in self))

    @property
    def edges(self):
        return edges(self)

    @property
    def edges_indices(self):
        s = len(self)
        return ((self.indices[i], self.indices[(i+1) % s]) for i in range(s))

    def prepare_bbox(self):
        self.bbox = BoundingBox.around(self)
        return self

    def winding_number(self, point):
        if self.bbox and not self.bbox.contains(point):
            return 0
        return winding_number(self, point)

    def contains(self, point):
        return self.winding_number(point) != 0

    def area(self, signed=False):
        return area(self, signed=signed)

    def centroid(self):
        if self._centroid is None:
            self._centroid = centroid(self)
        return self._centroid

