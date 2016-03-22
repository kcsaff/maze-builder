from maze_builder.meshes.mesh import MeshBuilder
from maze_builder.meshes.favaray import favaray_xml_element


class MeshIllustrator(object):
    def __init__(self, width=0.5, height=1, material=None, density=1):
        self.width = width
        self.height = height
        self.material = material
        self.density = density

    def draw(self, cubic):
        mesh = MeshBuilder()

        for i in range(cubic.maxx-cubic.minx+1):
            x = cubic.minx + i
            for j in range(cubic.maxy-cubic.miny+1):
                y = cubic.miny + j

                va = mesh.vertex((x, y, 0))
                vb = mesh.vertex((x+self.width, y, 0))
                vc = mesh.vertex((x+1, y, 0))
                vd = mesh.vertex((x, y+self.width, 0))
                ve = mesh.vertex((x+self.width, y+self.width, 0))
                vf = mesh.vertex((x+1, y+self.width, 0))
                vg = mesh.vertex((x, y+1, 0))
                vh = mesh.vertex((x+self.width, y+1, 0))
                vi = mesh.vertex((x+1, y+1, 0))
                vA = mesh.vertex((x, y, 0))
                vB = mesh.vertex((x+self.width, y, 0))
                vC = mesh.vertex((x+1, y, 0))
                vD = mesh.vertex((x, y+self.width, 0))
                vE = mesh.vertex((x+self.width, y+self.width, 0))
                vF = mesh.vertex((x+1, y+self.width, 0))
                vG = mesh.vertex((x, y+1, 0))
                vH = mesh.vertex((x+self.width, y+1, 0))
                vI = mesh.vertex((x+1, y+1, 0))

                #     g--h----i
                #    /| /|    |
                #   G-+H |    |  ^
                #   | |  |    |  +    Z
                #   | d--e----f  +   /
                #   |/  /|   /|  Y  L
                #   D--E |  F |
                #   |  | b--+-c    X+++++++>
                #   |  |/   |/
                #   A--B----C

                kwargs = dict(material=self.material, density=self.density)
                mesh.rectangle((vA, vB, vD), **kwargs)  # Junction roof
                mesh.rectangle((ve, vf, ve), **kwargs)  # Room floor
                if cubic.any_active_route_connecting((i, j, 0), (i-1, j, 0)):
                    # Draw corridor in -X direction
                    mesh.rectangle((vD, vE, vd), **kwargs)
                    mesh.rectangle((vd, ve, vg), **kwargs)
                    mesh.rectangle((vg, vh, vG), **kwargs)
                else:
                    # Draw wall in -X direction
                    mesh.rectangle((vd, vD, vg), **kwargs)
                    mesh.rectangle((vD, vE, vG), **kwargs)
                    mesh.rectangle((vE, ve, vH), **kwargs)
                if cubic.any_active_route_connecting((i, j, 0), (i, j-1, 0)):
                    # Draw corridor in -Y direction
                    mesh.rectangle((vB, vb, vE), **kwargs)
                    mesh.rectangle((vb, vc, ve), **kwargs)
                    mesh.rectangle((vc, vC, vf), **kwargs)
                else:
                    # Draw wall in -Y direction
                    mesh.rectangle((vb, vc, vB), **kwargs)
                    mesh.rectangle((vB, vC, vE), **kwargs)
                    mesh.rectangle((vE, vF, ve), **kwargs)

        return mesh


class FavarayIllustrator(MeshIllustrator):
    def draw(self, cubic):
        mesh = super().draw(cubic)
