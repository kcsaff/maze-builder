from maze_builder.meshes.mesh import MeshBuilder, MeshTransformation, MeshWarp
from maze_builder.meshes.scene import *
from maze_builder.meshes.yafaray import dump_yafaray
from maze_builder.meshes.obj import dump_obj
from maze_builder import random2
from .template import resource
import random

import io


class MeshIllustrator(object):
    def __init__(
        self,
        width=0.1, height=1, depth=0,
        material=None, density=1, enclosed=False,
        **attrs
    ):
        self.width = width
        self.depth = depth
        self.height = height
        self.material = material
        self.density = density
        self.enclosed = enclosed
        self.attrs = attrs

        self.rectangle_kwargs = dict(material=self.material, density=self.density)

    def _warp(self, v):
        x, y, z = v
        depth = self.depth(x, y) if callable(self.depth) else 0
        height = self.height(x, y) if callable(self.height) else 1

        return x, y, (1-z) * depth + z * height

    def _warp_enclosed(self, v, zmin=None, cubic=None):
        x, y, z = v
        depth = self.depth(x, y) if callable(self.depth) else 0
        height = self.height(x, y) if callable(self.height) else 1
        if z == 0 and (x <= cubic.minx or y <= cubic.miny or x > cubic.maxx+1 or y > cubic.maxy+1):
            return x, y, 0

        return x, y, ((1-z) * depth + z * height) - (zmin or 0)

    def _draw_room(self, cubic, mesh, coords, width, z0, z1, zmin):
        x, y, z = coords
        if z != cubic.maxz:
            raise RuntimeError('Illustrator only works for 2D')

        xbot = x == cubic.minx
        ybot = y == cubic.miny
        xtop = x == cubic.maxx+1
        ytop = y == cubic.maxy+1

        va = mesh.enter_vertex((x, y, z0))
        vb = mesh.enter_vertex((x + width, y, z0))
        vc = mesh.enter_vertex((x + 1, y, z0))
        vd = mesh.enter_vertex((x, y + width, z0))
        ve = mesh.enter_vertex((x + width, y + width, z0))
        vf = mesh.enter_vertex((x + 1, y + width, z0))
        vg = mesh.enter_vertex((x, y + 1, z0))
        vh = mesh.enter_vertex((x + width, y + 1, z0))
        vi = mesh.enter_vertex((x + 1, y + 1, z0))
        vA = mesh.enter_vertex((x, y, z1))
        vB = mesh.enter_vertex((x + width, y, z1))
        vC = mesh.enter_vertex((x + 1, y, z1))
        vD = mesh.enter_vertex((x, y + width, z1))
        vE = mesh.enter_vertex((x + width, y + width, z1))
        vF = mesh.enter_vertex((x + 1, y + width, z1))
        vG = mesh.enter_vertex((x, y + 1, z1))
        vH = mesh.enter_vertex((x + width, y + 1, z1))
        vI = mesh.enter_vertex((x + 1, y + 1, z1))

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

        kwargs = self.rectangle_kwargs
        mesh.rectangle((vA, vB, vD), **kwargs)  # Junction roof
        if not xtop and not ytop:
            mesh.rectangle((ve, vf, vh), **kwargs)  # Room floor

        if xtop:
            mesh.rectangle((vB, vb, vE), **kwargs)
        elif x == cubic.minx:
            mesh.rectangle((va, vA, vd), **kwargs)
        if not xtop and cubic.any_active_route_connecting((x, y, z), (x-1, y, z)):
            # Draw corridor in -X direction
            mesh.rectangle((vD, vE, vd), **kwargs)
            mesh.rectangle((vd, ve, vg), **kwargs)
            mesh.rectangle((vg, vh, vG), **kwargs)
        elif not ytop:
            # Draw wall in -X direction
            mesh.rectangle((vd, vD, vg), **kwargs)
            mesh.rectangle((vD, vE, vG), **kwargs)
            mesh.rectangle((vE, ve, vH), **kwargs)

        if ytop:
            mesh.rectangle((vD, vE, vd), **kwargs)
        elif y == cubic.miny:
            mesh.rectangle((va, vb, vA), **kwargs)
        if not ytop and cubic.any_active_route_connecting((x, y, z), (x, y-1, z)):
            # Draw corridor in -Y direction
            mesh.rectangle((vB, vb, vE), **kwargs)
            mesh.rectangle((vb, vc, ve), **kwargs)
            mesh.rectangle((vc, vC, vf), **kwargs)
        elif not xtop:
            # Draw wall in -Y direction
            mesh.rectangle((vb, vc, vB), **kwargs)
            mesh.rectangle((vB, vC, vE), **kwargs)
            mesh.rectangle((vE, vF, ve), **kwargs)

    def draw(self, cubic):
        mesh = MeshBuilder(**self.attrs)

        width = self.width() if callable(self.width) else self.width
        z1 = self.height if not callable(self.height) else 1
        z0 = self.depth if not callable(self.depth) else 0

        zmin = float('inf')
        for i in range(int(cubic.maxx - cubic.minx) + 3):
            x = cubic.minx + i
            for j in range(int(cubic.maxx - cubic.minx) + 3):
                y = cubic.miny + j
                height = self.depth(x, y)
                if height < zmin:
                    zmin = height

        for room in cubic.rooms:
            self._draw_room(cubic, mesh, room, width, z0, z1, zmin)

        for i in range(int(cubic.maxx - cubic.minx) + 1):
            x = cubic.minx + i
            self._draw_room(cubic, mesh, (x, cubic.maxy+1, cubic.minz), width, z0, z1, zmin)

        for j in range(int(cubic.maxx - cubic.minx) + 1):
            y = cubic.miny + j
            self._draw_room(cubic, mesh, (cubic.maxx+1, y, cubic.minz), width, z0, z1, zmin)

        self._draw_room(cubic, mesh, (cubic.maxx+1, cubic.maxy+1, cubic.minz), width, z0, z1, zmin)

        if self.enclosed:
            mesh.rectangle(
                [(cubic.minx, cubic.miny, 0), (cubic.minx, cubic.maxy+1+width, 0), (cubic.maxx+1+width, cubic.miny, 0)],
                material=self.material
            )

        if callable(self.height) or callable(self.depth):
            if self.enclosed:
                return MeshWarp(mesh, lambda v: self._warp_enclosed(v, zmin-width, cubic))
            else:
                return MeshWarp(mesh, self._warp)
        else:
            return mesh


class ObjIllustrator(MeshIllustrator):
    def draw(self, cubic, fp=None):
        mesh = super().draw(cubic)
        return dump_obj(fp, mesh)


class YafarayIllustrator(MeshIllustrator):
    def __init__(self, xml, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xml = xml

    def draw(self, cubic, fp=None):
        mesh = super().draw(cubic)
        scene = Scene()
        # Lights
        light_color = Color(1-random.random()**2.5,1-random.random()**2.5,1-random.random()**1.5)
        ambience_color = (1-random.random()**1.5) * (Color.WHITE - light_color)
        sky_color = ambience_color.blowout(1-random.random()*random.random()*random.random())
        scene.set_background(sky_color)
        scene.set_ambience(Ambience(ambience_color))
        scene.add_light(Light(random2.hemisphere(1, minz=0.001, maxz=0.6), Color.WHITE, 0.5+random.random(), type='sunlight'))
        # Camera
        camera_location = random2.hemisphere(40, minz=1)
        print(camera_location)
        _, maxz = mesh.find_limits(
            (0, 0, 1),
            xbounds=(
                max((cubic.minx+1, camera_location[0]-1)),
                min((cubic.maxx-2, camera_location[0]+1)),
            ),
            ybounds=(
                max((cubic.miny+1, camera_location[1]-1)),
                min((cubic.maxy-2, camera_location[1]+1)),
            )
        )
        print('Camera limit {}'.format(maxz))
        if maxz > -float('inf'):
            camera_location = (camera_location[0], camera_location[1], camera_location[2] + maxz)
        cminz, cmaxz = mesh.find_limits((0, 0, 1), xbounds=(-1, 1), ybounds=(-1, 1))
        look_at = (0, 0, random.random() * (cminz + cmaxz)/2)
        print(look_at)
        scene.set_camera(Camera(camera_location, look_at))
        # Action
        scene.add_mesh(mesh)
        return dump_yafaray(fp, resource(self.xml), scene, material_map={None: 'defaultMat'})
