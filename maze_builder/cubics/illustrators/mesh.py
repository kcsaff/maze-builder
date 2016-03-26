from maze_builder.meshes.mesh import MeshBuilder, MeshTransformation, MeshWarp
from maze_builder.meshes.scene import *
from maze_builder.meshes.yafaray import dump_yafaray
from maze_builder.meshes.obj import dump_obj
from maze_builder import random2
from .template import resource
import random
from maze_builder.util import timed, is_verbose

import io


YAFARAY_FILENAME = 'out.yafaray.xml'


OBJ_FILENAME = 'out.obj'


class Mesher2D(object):
    def __init__(
        self,
        wall=0.1,
        material=None, density=1, enclosed=False,
        **attrs
    ):
        self.wall = wall
        self.material = material
        self.density = density
        self.enclosed = enclosed
        self.attrs = attrs

        self.rectangle_kwargs = dict(material=self.material, density=self.density)

    def __call__(self, cubic):
        return self.draw(cubic)

    def draw(self, cubic):
        with timed(is_verbose(1), 'Meshing maze...', 'Maze generated in {0:.3f}s'):
            mesh = MeshBuilder(**self.attrs)

            wall = self.wall() if callable(self.wall) else self.wall

            for room in cubic.rooms:
                self._draw_room(cubic, mesh, room, wall)

            for i in range(int(cubic.maxx - cubic.minx) + 1):
                x = cubic.minx + i
                self._draw_room(cubic, mesh, (x, cubic.maxy+1, cubic.minz), wall)

            for j in range(int(cubic.maxx - cubic.minx) + 1):
                y = cubic.miny + j
                self._draw_room(cubic, mesh, (cubic.maxx+1, y, cubic.minz), wall)

            self._draw_room(cubic, mesh, (cubic.maxx+1, cubic.maxy+1, cubic.minz), wall)

            return mesh

    def _draw_room(self, cubic, mesh, coords, wall):
        x, y, z = coords
        if z != cubic.maxz:
            raise RuntimeError('Illustrator only works for 2D')

        xbot = x == cubic.minx
        ybot = y == cubic.miny
        xtop = x == cubic.maxx+1
        ytop = y == cubic.maxy+1

        va = mesh.enter_vertex((x, y, z))
        vb = mesh.enter_vertex((x + wall, y, z))
        vc = mesh.enter_vertex((x + 1, y, z))
        vd = mesh.enter_vertex((x, y + wall, z))
        ve = mesh.enter_vertex((x + wall, y + wall, z))
        vf = mesh.enter_vertex((x + 1, y + wall, z))
        vg = mesh.enter_vertex((x, y + 1, z))
        vh = mesh.enter_vertex((x + wall, y + 1, z))
        vi = mesh.enter_vertex((x + 1, y + 1, z))
        vA = mesh.enter_vertex((x, y, z+1))
        vB = mesh.enter_vertex((x + wall, y, z+1))
        vC = mesh.enter_vertex((x + 1, y, z+1))
        vD = mesh.enter_vertex((x, y + wall, z+1))
        vE = mesh.enter_vertex((x + wall, y + wall, z+1))
        vF = mesh.enter_vertex((x + 1, y + wall, z+1))
        vG = mesh.enter_vertex((x, y + 1, z+1))
        vH = mesh.enter_vertex((x + wall, y + 1, z+1))
        vI = mesh.enter_vertex((x + 1, y + 1, z+1))

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
        elif xbot:
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
        elif ybot:
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


class Warper2D(object):
    def __init__(self, noise, args=(), scale=1, height=1, offset=(0, 0)):
        self.noise = noise
        self.args = args
        self.scale = scale
        self.height = height
        self.offset = offset

    def __call__(self, mesh):
        with timed(is_verbose(1), 'Warping mesh...', 'Mesh warped in {0:.3f}s'):
            args = self.args() if callable(self.args) else self.args
            scale = self.scale() if callable(self.scale) else self.scale
            height = self.height() if callable(self.height) else self.height
            offx, offy = self.offset() if callable(self.offset) else self.offset

            def warp(v):
                x, y, z = v
                z += height * scale * self.noise(offx + x / scale, offy + y / scale, *args)
                return x, y, z

            mesh.perform_warp(warp)
            return mesh


class SceneWrapper(object):
    def __call__(self, mesh):
        scene = Scene()
        scene.add_mesh(mesh)
        return scene


class RandomSunMaker(object):
    def __call__(self, scene):
        light_color = Color(1-random.random()**2.5,1-random.random()**2.5,1-random.random()**1.5)
        ambience_color = (1-random.random()**1.5) * (Color.WHITE - light_color)
        sky_color = ambience_color.blowout(1-random.random()*random.random()*random.random())
        scene.set_background(sky_color)
        scene.set_ambience(Ambience(ambience_color))
        scene.add_light(Light(random2.hemisphere(1, minz=0.001, maxz=0.6), Color.WHITE, 0.5+random.random(), type='sunlight'))
        return scene


class RandomCameraPlacer(object):
    def __init__(self, resolution=(1024, 512)):
        self.resolution = resolution

    def __call__(self, scene):
        mesh = scene.meshes[0]

        minx, maxx = mesh.find_limits((1, 0, 0))
        miny, maxy = mesh.find_limits((0, 1, 0))

        radius = 1 + random.random() * min((maxx-minx, maxy-miny))
        camera_location = random2.hemisphere(radius, minz=1)

        _, maxz = mesh.find_limits(
            (0, 0, 1),
            xbounds=(
                max((minx+1, camera_location[0]-1)),
                min((maxx-1, camera_location[0]+1)),
            ),
            ybounds=(
                max((miny+1, camera_location[1]-1)),
                min((maxy-2, camera_location[1]+1)),
            )
        )
        print('Camera limit {}'.format(maxz))
        if maxz > -float('inf'):
            camera_location = (camera_location[0], camera_location[1], camera_location[2] + maxz)
        cminz, cmaxz = mesh.find_limits((0, 0, 1), xbounds=(-1, 1), ybounds=(-1, 1))
        look_at = (0, 0, random.random() * (cminz + cmaxz)/2)

        scene.set_camera(Camera(camera_location, look_at, resolution=self.resolution))

        return scene


class ObjSaver(object):
    def __init__(self, filename=OBJ_FILENAME):
        self.filename = filename

    def __call__(self, mesh):
        if isinstance(mesh, Scene):
            mesh = mesh.meshes[0]
        with open(self.filename, 'w') as f:
            dump_obj(f, mesh)
        return self.filename


class YafaraySaver(object):
    def __init__(self, filename=YAFARAY_FILENAME, material_map=None, xml='simple.yafaray.xml'):
        self.filename = filename
        self.material_map = material_map or {None: 'defaultMat'}
        self.xml = xml

    def __call__(self, scene):
        with timed(is_verbose(1), 'Saving scene to yafaray XML format...', 'Scene saved in {0:.3f}s'):
            dump_yafaray(self.filename, resource(self.xml), scene, material_map={None: 'defaultMat'})
            return self.filename
