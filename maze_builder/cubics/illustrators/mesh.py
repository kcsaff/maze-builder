from maze_builder.meshes.mesh import MeshBuilder, MeshTransformation, MeshWarp
from maze_builder.meshes.scene import *
from maze_builder.meshes.yafaray import dump_yafaray
from maze_builder.meshes.obj import dump_obj, read_obj
from maze_builder.meshes.stl import read_binary_stl
from maze_builder import random2
from .template import resource
import random
from maze_builder.util import timed, is_verbose

import io


YAFARAY_FILENAME = 'out.yafaray.xml'


OBJ_FILENAME = 'out.obj'


class MeshFeatures(object):
    def __init__(self, filename):
        self.filename = filename

    def __call__(self, x, y, z=None):
        filename = self.filename
        if filename.endswith('stl'):
            mesh = read_binary_stl(filename)
        elif filename.endswith('obj'):
            mesh = read_obj(filename)
        else:
            mesh = None

        def warp1(v):
            return (-v[0], v[2], v[1])
        mesh.vertices.warp(warp1)

        minx = min(v[0] for v in mesh.vertices)
        maxx = max(v[0] for v in mesh.vertices)
        miny = min(v[1] for v in mesh.vertices)
        maxy = max(v[1] for v in mesh.vertices)
        minz = min(v[2] for v in mesh.vertices)
        maxz = max(v[2] for v in mesh.vertices)
        ox = (minx + maxx) / 2
        oy = (miny + maxy) / 2
        sx = x / (maxx - minx)
        sy = y / (maxy - miny)
        s = min((sx, sy))

        def warp2(v):
            return (
                (v[0] - minx) * s,
                (v[1] - miny) * s,
                (v[2] - minz) * s,
            )
        mesh.vertices.warp(warp2)
        return mesh


class Mesher2D(object):
    def __init__(
        self,
        wall=0.1,
        material=None, density=1, enclosed=False,
        features=None,
        profile=[(0,1),(1,1)],
        floor=True,
        height=1,
        **attrs
    ):
        self.wall = wall
        self.material = material
        self.density = density
        self.enclosed = enclosed
        self.attrs = attrs
        self.features = features
        self.profile = profile
        self.floor = floor
        self.height = height

        self.rectangle_kwargs = dict(material=self.material, density=self.density)

    def __call__(self, cubic):
        return self.draw(cubic)

    def draw(self, cubic):
        meshes = list()
        with timed(is_verbose(1), 'Meshing maze...', 'Maze generated in {0:.3f}s'):
            mesh = MeshBuilder(**self.attrs)

            profile = self.profile() if callable(self.profile) else self.profile
            wall = self.wall() if callable(self.wall) else self.wall
            height = self.height() if callable(self.height) else self.height

            for room in cubic.rooms:
                self._draw_room(cubic, mesh, room, wall, height, profile)

            for i in range(int(cubic.maxx - cubic.minx) + 1):
                x = cubic.minx + i
                self._draw_room(cubic, mesh, (x, cubic.maxy+1, cubic.minz),
                                wall, height, profile)

            for j in range(int(cubic.maxx - cubic.minx) + 1):
                y = cubic.miny + j
                self._draw_room(cubic, mesh, (cubic.maxx+1, y, cubic.minz),
                                wall, height, profile)

            self._draw_room(cubic, mesh,
                            (cubic.maxx+1, cubic.maxy+1, cubic.minz),
                            wall, height, profile)

            meshes.append(mesh)

            hall = 1 - wall
            if self.features:
                for feature in cubic.features:
                    p0 = (feature.minx, feature.miny)
                    p1 = (1 + feature.maxx, 1 + feature.maxy)
                    x0 = (p0[0] + 1) * (hall + wall)
                    y0 = (p0[1] + 1) * (hall + wall)
                    x1 = (p1[0] - 1) * (hall + wall) + wall
                    y1 = (p1[1] - 1) * (hall + wall) + wall

                    fmesh = self.features(x1 - x0, y1 - y0)

                    def warp(v):
                        return (v[0]+x0, v[1]+y0, v[2]+cubic.minz)

                    fmesh.vertices.warp(warp)
                    meshes.append(fmesh)

        return meshes

    def _draw_room(self, cubic, mesh, coords, wall, height, profile):
        x, y, z = coords
        if z != cubic.maxz:
            raise RuntimeError('Illustrator only works for 2D')

        xbot = x == cubic.minx
        ybot = y == cubic.miny
        xtop = x == cubic.maxx+1
        ytop = y == cubic.maxy+1

        w2 = wall / 2

        va = [mesh.enter_vertex((x-p*w2, y-p*w2, z+h*height)) for (h, p) in profile]
        vb = [mesh.enter_vertex((x+p*w2, y-p*w2, z+h*height)) for (h, p) in profile]
        vc = [mesh.enter_vertex((x+1-p*w2, y-p*w2, z+h*height)) for (h, p) in profile]
        vd = [mesh.enter_vertex((x-p*w2, y+p*w2, z+h*height)) for (h, p) in profile]
        ve = [mesh.enter_vertex((x+p*w2, y+p*w2, z+h*height)) for (h, p) in profile]
        vf = [mesh.enter_vertex((x+1-p*w2, y+p*w2, z+h*height)) for (h, p) in profile]
        vg = [mesh.enter_vertex((x-p*w2, y+1-p*w2, z+h*height)) for (h, p) in profile]
        vh = [mesh.enter_vertex((x+p*w2, y+1-p*w2, z+h*height)) for (h, p) in profile]
        vi = [mesh.enter_vertex((x+1-p*w2, y+1-p*w2, z+h*height)) for (h, p) in profile]

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
        mesh.rectangle((va[-1], vb[-1], vd[-1]), **kwargs)  # Junction roof
        if self.floor and not xtop and not ytop:
            mesh.rectangle((ve[0], vf[0], vh[0]), **kwargs)  # Room floor

        has_x_hall = cubic.any_active_route_connecting((x, y, z), (x-1, y, z))
        has_y_hall = cubic.any_active_route_connecting((x, y, z), (x, y-1, z))

        for i in range(len(profile) - 1):
            first = not i
            if xtop:
                mesh.rectangle((vb[i+1], vb[i], ve[i+1]), **kwargs)
            elif xbot:
                mesh.rectangle((va[i], va[i+1], vd[i]), **kwargs)

            if not xtop and has_x_hall:
                # Draw corridor in -X direction
                mesh.rectangle((vd[i+1], ve[i+1], vd[i]), **kwargs)
                if self.floor and first:
                    mesh.rectangle((vd[0], ve[0], vg[0]), **kwargs)
                mesh.rectangle((vg[i], vh[i], vg[i+1]), **kwargs)
            elif not ytop:
                # Draw wall in -X direction
                mesh.rectangle((vd[i], vd[i+1], vg[i]), **kwargs)
                if first:
                    mesh.rectangle((vd[-1], ve[-1], vg[-1]), **kwargs)
                mesh.rectangle((ve[i+1], ve[i], vh[i+1]), **kwargs)

            if ytop:
                mesh.rectangle((vd[i+1], ve[i+1], vd[i]), **kwargs)
            elif ybot:
                mesh.rectangle((va[i], vb[i], va[i+1]), **kwargs)
            if not ytop and has_y_hall:
                # Draw corridor in -Y direction
                mesh.rectangle((vb[i+1], vb[i], ve[i+1]), **kwargs)
                if self.floor and first:
                    mesh.rectangle((vb[0], vc[0], ve[0]), **kwargs)
                mesh.rectangle((vc[i], vc[i+1], vf[i]), **kwargs)
            elif not xtop:
                # Draw wall in -Y direction
                mesh.rectangle((vb[i], vc[i], vb[i+1]), **kwargs)
                if first:
                    mesh.rectangle((vb[-1], vc[-1], ve[-1]), **kwargs)
                mesh.rectangle((ve[i+1], vf[i+1], ve[i]), **kwargs)


class MultiMesher(object):
    def __init__(self, meshers):
        self.meshers = meshers

    def __call__(self, cubic):
        return self.draw(cubic)

    def draw(self, cubic):
        meshes = list()
        for mesher in self.meshers:
            meshes.extend(mesher(cubic))
        return meshes


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
            mesh.update_attributes(smoothing_degrees=30)
            return mesh


class SceneWrapper(object):
    def __call__(self, meshes):
        scene = Scene()
        for mesh in meshes:
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
    def __init__(self, resolution=(1024, 512), distance_scale=0.75):
        self.resolution = resolution
        self.distance_scale = distance_scale

    def __call__(self, scene):
        mesh = scene.meshes[0]

        minx, maxx = mesh.find_limits((1, 0, 0))
        miny, maxy = mesh.find_limits((0, 1, 0))

        radius = 1 + random.random() * min((maxx-minx, maxy-miny)) * self.distance_scale
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
