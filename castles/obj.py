from .faces import V, Face, Surface


class VertexCounter(object):
    def __init__(self):
        self.vcoords = dict()
        self.lcoords = list()

    def find(self, vertex):
        coords = V.fix(vertex).coords
        if coords not in self.vcoords:
            return self.put(vertex)
        return self.vcoords[coords]

    def put(self, vertex):
        coords = V.fix(vertex).coords
        result = 1 + len(self.vcoords)
        self.vcoords[coords] = result
        self.lcoords.append(coords)
        return result

    def get(self, n):
        return self.lcoords[n-1]

    def write(self, stream):
        for coords in self.lcoords:
            stream.write('v {}\n'.format(' '.join(str(c) for c in coords)))


def write_obj(surface, stream):
    vcounter = VertexCounter()
    for face in surface:
        for v in face:
            vcounter.find(v)
    vcounter.write(stream)
    for face in surface:
        stream.write('f {}\n'.format(' '.join(str(vcounter.find(v)) for v in face)))


def read_obj(stream):
    vcounter = VertexCounter()
    faces = list()
    unknown = set()
    for line in stream:
        command, arg = line.strip().split(1)
        args = arg.strip().split()
        if command == 'v':
            vcounter.put(V(float(a) for a in args))
        elif command == 'f':
            faces.append(Face(vcounter.get(int(a)) for a in args))
        elif command not in unknown:
            unknown.add(command)
            print('Unknown command {}'.format(command))
    return Surface(faces)
