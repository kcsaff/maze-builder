import math
from numbers import Number


INFINITE_POWER = 24  # ~=~ When is a power close to inf?


class Vertex(object):
    def __init__(self, coords):
        self.coords = tuple(coords)
        if self.coords and not isinstance(self.coords[0], Number):
            raise RuntimeError

    @classmethod
    def fix(cls, vertex):
        return vertex if isinstance(vertex, cls) else cls(vertex)

    def apply(self, fun, origin=0):
        return fun(self - origin) + origin

    def dot(self, other):
        return sum(c0 * c1 for c0, c1 in zip(self, other))

    def __repr__(self):
        return 'V({})'.format(self.coords)

    def cross(self, other):
        return V((
            self[1] * other[2] - self[2] * other[1],
            self[2] * other[0] - self[0] * other[2],
            self[0] * other[1] - self[1] * other[0],
        ))

    def angle(self, other):
        other = Vertex.fix(other)
        cos_theta = self.dot(other) / self.norm() / other.norm()
        return math.acos(cos_theta)

    def norm(self, p=2):
        if p >= INFINITE_POWER:
            return max(abs(c) for c in self)
        elif p <= -INFINITE_POWER:
            return min(abs(c) for c in self)
        else:  # "normal" case
            return sum(abs(c)**p for c in self)**(1.0/p)

    def normalize(self, p=2):
        return self / self.norm(p=p)

    def __bool__(self):
        return any(self)

    def __len__(self):
        return len(self.coords)

    def __iter__(self):
        return iter(self.coords)

    def __getitem__(self, item):
        return self.coords[item]

    def __eq__(self, other):
        return self.coords == Vertex.fix(other).coords

    def __mul__(self, scalar):
        return self if scalar == 1 else Vertex(scalar * c for c in self)

    def __rmul__(self, scalar):
        return self * scalar

    def __truediv__(self, scalar):
        return self if scalar == 1 else self * (1 / scalar)

    def __neg__(self):
        return self * -1

    def __add__(self, other):
        return self if not other else Vertex(c0 + c1 for c0, c1 in zip(self, other))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self if not other else Vertex(c0 - c1 for c0, c1 in zip(self, other))

    def __rsub__(self, other):
        return other + -self


V = Vertex
V.O = Vertex((0, 0, 0))
V.I = Vertex((1, 0, 0))
V.J = Vertex((0, 1, 0))
V.K = Vertex((0, 0, 1))


def _radians(v, radians=None, degrees=None):
    if degrees is not None or radians is not None:
        return (radians or 0) + math.radians(degrees or 0)
    else:
        return V.fix(v).norm()


class Matrix(object):
    def __init__(self, rows):
        self.rows = [V.fix(row) for row in rows]

    @classmethod
    def rotation(cls, v, radians=None, degrees=None):
        r = _radians(v, radians=radians, degrees=degrees)
        q0 = math.cos(r/2)
        q1 = math.sin(r/2) * v[0]
        q2 = math.sin(r/2) * v[1]
        q3 = math.sin(r/2) * v[2]

        return cls((
            (q0*q0 + q1*q1 - q2*q2 - q3*q3, 2*(q1*q2 - q0*q3),             2*(q1*q3 + q0*q2)),
            (2*(q2*q1 + q0*q3),             q0*q0 - q1*q1 + q2*q2 - q3*q3, 2*(q2*q3 - q0*q1)),
            (2*(q3*q1 - q0*q2),             2*(q3*q2 + q0*q1),             q0*q0 - q1*q1 - q2*q2 + q3*q3),
        ))

    def __call__(self, v):
        return V(row.dot(v) for row in self.rows)


class Face(object):
    def __init__(self, vertices):
        self.vertices = tuple(Vertex.fix(vertex) for vertex in vertices)

    @classmethod
    def parallelogram(cls, e0, e1):
        return cls((
            V.O, V.O + e0, V.O + e0 + e1, V.O + e1
        ))

    def apply(self, fun, origin=0):
        return Face(v.apply(fun, origin=origin) for v in self)

    def __iter__(self):
        return iter(self.vertices)

    def __len__(self):
        return len(self.vertices)

    def __getitem__(self, item):
        return self.vertices[item]

    def slice(self, i, j):
        if i < j:
            return Face(self.vertices[i:j+1])
        else:
            return Face(self.vertices[i:] + self.vertices[:j+1])

    def center(self):
        return sum(self) / len(self)

    def edge(self, item):
        return self.vertices[(item + 1) % len(self)] - self.vertices[item % len(self)]

    def normal(self, item=None):
        if item is not None:
            return self.edge(item - 1).cross(self.edge(item))
        else:
            return sum(self.normal(i) for i in range(len(self))) / len(self)

    def translate(self, direction):
        return Face(v + direction for v in self)

    def direct(self, direction):
        return self if self.normal().dot(direction) > 0 else Face(reversed(self.vertices))

    def is_convex(self):
        normal = self.normal()
        for i in range(len(self)):
            if normal.dot(self.normal(i)) < 0:
                return False
        else:
            return True

    def triangulate(self):
        """Decompose into triangular faces."""
        if len(self.vertices) <= 3:
            yield self
        elif self.is_convex():
            split = len(self) // 2
            yield from self.slice(0, split)
            yield from self.slice(split, 0)
        else:
            raise NotImplementedError('Only implemented on convex faces')


class Surface(object):
    def __init__(self, faces):
        self.faces = list(faces)

    @classmethod
    def prism(cls, e0, e1, e2):
        return cls((
            Face.parallelogram(e0, e1).direct(-e2),
            Face.parallelogram(e1, e2).direct(-e0),
            Face.parallelogram(e2, e0).direct(-e1),
            Face.parallelogram(e0, e1).translate(e2).direct(e2),
            Face.parallelogram(e1, e2).translate(e0).direct(e0),
            Face.parallelogram(e2, e0).translate(e1).direct(e1),
        ))

    @classmethod
    def box(cls, x, y, z):
        return cls.prism(V.I * x, V.J * y, V.K * z)

    def __iter__(self):
        return iter(self.faces)

    def __len__(self):
        return len(self.faces)

    def __add__(self, other):
        return self if other is 0 else Surface(self.faces + other.faces)

    def __radd__(self, other):
        return self.__add__(other)

    def translate(self, direction):
        return Surface(f.translate(direction) for f in self)

    def apply(self, fun, origin=0):
        return Surface(face.apply(fun, origin=origin) for face in self)

    def rotate(self, normal, radians=None, degrees=None, origin=None):
        return self.apply(Matrix.rotation(normal, radians=radians, degrees=degrees), origin=origin)

    def triangulate(self):
        for face in self.faces:
            yield from face.triangulate()

