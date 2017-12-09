import struct
from .mesh import MeshBuilder


STL_BINARY_HEADER = struct.Struct('<80xI')

STL_TRIANGLE = struct.Struct('<12fIH')


def read_binary_stl(filename):
    mb = MeshBuilder()
    with open(filename, 'rb') as f:
        header = STL_BINARY_HEADER.unpack(f.read(STL_BINARY_HEADER.size))
        for i in range(header[0]):
            face = STL_TRIANGLE.unpack(f.read(STL_TRIANGLE.size))
            mb.enter_face(
                face[3:6],
                face[6:9],
                face[9:12]
            )
            f.read(face[12])

    return mb
