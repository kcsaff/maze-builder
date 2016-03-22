from maze_builder.meshes.mesh import MeshBuilder, MeshTransformation, MeshWarp
from maze_builder.meshes.yafaray import dump_yafaray
from maze_builder.meshes.obj import dump_obj
from .template import resource

import io


class MeshIllustrator(object):
    def __init__(self, width=0.1, height=1, depth=0, material=None, density=1, **attrs):
        self.width = width
        self.depth = depth
        self.height = height
        self.material = material
        self.density = density
        self.attrs = attrs

    def _warp(self, v):
        x, y, z = v
        depth = self.depth(x, y) if callable(self.depth) else 0
        height = self.height(x, y) if callable(self.height) else 1
        return x, y, (1-z) * depth + z * height

    def draw(self, cubic):
        mesh = MeshBuilder(**self.attrs)

        width = self.width() if callable(self.width) else self.width
        z1 = self.height if not callable(self.height) else 1
        z0 = self.depth if not callable(self.depth) else 0

        for x, y, z in cubic.rooms:
            if z != cubic.maxz:
                raise RuntimeError('Illustrator only works for 2D')

            va = mesh.vertex((x, y, z0))
            vb = mesh.vertex((x+width, y, z0))
            vc = mesh.vertex((x+1, y, z0))
            vd = mesh.vertex((x, y+width, z0))
            ve = mesh.vertex((x+width, y+width, z0))
            vf = mesh.vertex((x+1, y+width, z0))
            vg = mesh.vertex((x, y+1, z0))
            vh = mesh.vertex((x+width, y+1, z0))
            vi = mesh.vertex((x+1, y+1, z0))
            vA = mesh.vertex((x, y, z1))
            vB = mesh.vertex((x+width, y, z1))
            vC = mesh.vertex((x+1, y, z1))
            vD = mesh.vertex((x, y+width, z1))
            vE = mesh.vertex((x+width, y+width, z1))
            vF = mesh.vertex((x+1, y+width, z1))
            vG = mesh.vertex((x, y+1, z1))
            vH = mesh.vertex((x+width, y+1, z1))
            vI = mesh.vertex((x+1, y+1, z1))

            #     g--h----i     ^
            #    /| /|    |     +
            #   G-+H |    |     Y
            #   | |  |    |
            #   | d--e----f     Z   X+++>
            #   |/  /|   /|    X
            #   D--E |  F |   X
            #   |  | b--+-c  L
            #   |  |/   |/
            #   A--B----C

            kwargs = dict(material=self.material, density=self.density)
            mesh.rectangle((vA, vB, vD), **kwargs)  # Junction roof
            mesh.rectangle((ve, vf, vh), **kwargs)  # Room floor
            if cubic.any_active_route_connecting((x, y, z), (x-1, y, z)):
                # Draw corridor in -X direction
                mesh.rectangle((vD, vE, vd), **kwargs)
                mesh.rectangle((vd, ve, vg), **kwargs)
                mesh.rectangle((vg, vh, vG), **kwargs)
            else:
                # Draw wall in -X direction
                mesh.rectangle((vd, vD, vg), **kwargs)
                mesh.rectangle((vD, vE, vG), **kwargs)
                mesh.rectangle((vE, ve, vH), **kwargs)
            if cubic.any_active_route_connecting((x, y, z), (x, y-1, z)):
                # Draw corridor in -Y direction
                mesh.rectangle((vB, vb, vE), **kwargs)
                mesh.rectangle((vb, vc, ve), **kwargs)
                mesh.rectangle((vc, vC, vf), **kwargs)
            else:
                # Draw wall in -Y direction
                mesh.rectangle((vb, vc, vB), **kwargs)
                mesh.rectangle((vB, vC, vE), **kwargs)
                mesh.rectangle((vE, vF, ve), **kwargs)

        if callable(self.height) or callable(self.depth):
            return MeshWarp(mesh, self._warp)
        else:
            return mesh


class ObjIllustrator(MeshIllustrator):
    def draw(self, cubic):
        mesh = super().draw(cubic)
        return dump_obj(None, mesh)


class YafarayIllustrator(MeshIllustrator):
    def __init__(self, xml, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xml = xml

    def draw(self, cubic, fp=None):
        mesh = super().draw(cubic)
        if fp:
            dump_yafaray(fp, mesh, resource(self.xml), material_map={None: 'defaultMat'})
        else:
            return dump_yafaray(None, mesh, resource(self.xml), material_map={None: 'defaultMat'})
