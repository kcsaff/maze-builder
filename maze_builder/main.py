import argparse
import os.path
from .processor import Processor, PipelineBuilder
import sys
from collections import namedtuple
import shutil
import random
import math
import noise
from .sewer import Choice


POVRAY_INI = 'povray.ini'


Settings = namedtuple(
    'Settings',
    ['config', 'verbose', 'keys',
     'pov', 'ini', 'include_path',
     'magick',
     'builder', 'tweet', 'autofollow',
     'yafaray', 'yafaray_plugins',
     'emojis',
     ]
)


DEFAULTS = Settings(
    config=None,
    verbose=0,
    keys=None,
    pov=None,
    ini=None,
    include_path=None,
    magick=None,
    builder=Choice.DEFAULT,
    tweet=False,  # Misleading, change this
    autofollow=False,
    yafaray=None,
    yafaray_plugins=None,
    emojis=None,
)


# Default executables, used only if we detect their presence.
PROG_DEFAULTS = dict(
    pov='povray',
    magick='convert',
)


parser = argparse.ArgumentParser('Forgotten Castles Bot')
parser.add_argument(
    '--config', '-c', type=str,
    help='Config file to load (default) arguments from'
)
parser.add_argument(
    '--verbose', '-v', action='count',
    help='More v\'s, more verbose (up to 4)'
)
parser.add_argument(
    '--keys', '-k', type=str,
    help='Keys file needed to post to Twitter',
)
parser.add_argument(
    '--emojis', type=str, default=None,
    help='Path to emoji zip file',
)
parser.add_argument(
    '--pov', '-P', type=str,
    help='Path to POV-Ray executable',
)
parser.add_argument(
    '--ini', '-i', type=str,
    help='INI file to pass to POV-Ray -- a random choice will be made for comma-separated filenames',
)
parser.add_argument(
    '--include-path', '-I', type=str,
    help='POV-Ray include path(s), comma-separated',
)
parser.add_argument(
    '--magick', '-M', type=str,
    help='ImageMagick command line tool',
)
parser.add_argument(
    '--builder', '-b', type=str, default=Choice.DEFAULT,
    help='Force particular builder to be used',
)
parser.add_argument(
    '--yafaray', '-Y', type=str,
    help='Yafaray executable',
)

parser.add_argument(
    '--tweet', '-T',
    action='store_true', default=False,
    help='Tweet already rendered image',
)

parser.add_argument(
    '--autofollow', '-A',
    action='store_true', default=False,
    help='Auto-follow my followers',
)


def _find_config(filename):
    if os.path.exists(filename):
        return os.path.abspath(filename)
    candidate = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), filename)
    if os.path.exists(candidate):
        return os.path.abspath(candidate)
    return None


def make_defaults():
    return DEFAULTS._replace(**{
        arg: prog for arg, prog in PROG_DEFAULTS.items() if shutil.which(prog)
    })


def main(args=None):
    # Rigamarole of loading args from config (if any) & setting as defaults
    defaults = make_defaults()

    args = defaults._replace(**vars(args)) if args else defaults
    knargs, _ = parser.parse_known_args()
    if knargs.config:
        from .config import read_config
        args = args._replace(**vars(read_config(knargs.config)))

    if not knargs.ini and not args.ini:
        args = args._replace(ini=_find_config(POVRAY_INI))
    if not knargs.ini and not args.ini:
        args = args._replace(ini=_find_config(POVRAY_INI))

    parser.set_defaults(**vars(args))
    args = parser.parse_args()

    if args.verbose >= 4:
        for key, value in sorted(vars(args).items()):
            print('{}: {}'.format(key, value))

    for prog in PROG_DEFAULTS:
        executable = getattr(args, prog)
        if executable and not shutil.which(executable):
            raise RuntimeError('Executable {} not found!'.format(executable))

    # Make & run processor

    from maze_builder.sewer import Choice
    from maze_builder.castles.builder import CastleBuilder
    from maze_builder.castles.illustrators import TemplateIllustrator
    from maze_builder.cubics.builders import (
        ImageBuilder, CubicPovBuilder, ImageBuilderCombined, SeededPovBuilder,
        FilledCubicGenerator, ImageSaver, TextSaver
    )
    from maze_builder.cubics.illustrators.template import CubicTemplateIllustrator
    from maze_builder.cubics.illustrators.imaging import (
        ImageBlockIllustratorZoomed, ImageLineIllustrator
    )
    from maze_builder.cubics.illustrators.mesh import (
        Mesher2D, Warper2D, SceneWrapper, MeshFeatures,
        RandomCameraPlacer, RandomSunMaker, YafaraySaver, ObjSaver,
        MultiMesher

    )
    from maze_builder.lost_text.writers import LostTextWriter
    from maze_builder.meshes.material import read_mtl

    builders = {
        CastleBuilder(TemplateIllustrator('evil.pov.jinja2')): 'evil',
        CastleBuilder(TemplateIllustrator('fantasy.pov.jinja2')): 'fantasy',
        CastleBuilder(TemplateIllustrator('escher.pov.jinja2')): 'escher',
        CastleBuilder(TemplateIllustrator('brick.pov.jinja2')): 'brick',
        CastleBuilder(TemplateIllustrator('pure.pov.jinja2')): 'pure',
        ImageBuilder(506, 253): 'bw2d',
        ImageBuilder(506, 253, illustrator=ImageBlockIllustratorZoomed()): 'bw2dtilt',
        ImageBuilderCombined(512, 512, (
            ImageBlockIllustratorZoomed(hall_colors=[(255,0,0)], size=(506, 253)),
            ImageBlockIllustratorZoomed(hall_colors=[(0,255,0)], size=(506, 253)),
            ImageBlockIllustratorZoomed(hall_colors=[(0,0,255)], size=(506, 253)),
        ), 'add'): 'colors2d',
        ImageBuilderCombined(512, 512, (
            ImageBlockIllustratorZoomed(wall_colors=[tuple(int(256*(1-random.random()**2)) for _ in range(3))], size=(506, 253)),
            ImageBlockIllustratorZoomed(wall_colors=[tuple(int(256*(1-random.random()**2)) for _ in range(3))], size=(506, 253)),
            ImageBlockIllustratorZoomed(wall_colors=[tuple(int(256*(1-random.random()**2)) for _ in range(3))], size=(506, 253)),
        ), 'multiply'): 'pastels2d',
        CubicPovBuilder(CubicTemplateIllustrator('boulders.pov.jinja2'), 50): 'boulders',
        CubicPovBuilder(CubicTemplateIllustrator('simple.pov.jinja2'), 50): 'simple3d',
        CubicPovBuilder(CubicTemplateIllustrator('borg.pov.jinja2'), 8, 8, 8): 'borg',
        SeededPovBuilder(CubicTemplateIllustrator('borg.pov.jinja2')): 'borg2',
    }

    noise_amount = 2
    noise_scale = 2**noise_amount
    noise_x = 1000 * random.random()
    noise_y = 1000 * random.random()

    builders.update({
        PipelineBuilder(
            FilledCubicGenerator(70),
            Mesher2D(wall=random.random, density=2),
            Choice({
                Warper2D(
                    noise.pnoise2,
                    (3,),
                    (lambda: 40 * random.random()),
                    (lambda: random.random() ** 2.5),
                    (noise_x, noise_y)
                ): 10,
                (lambda mesh: mesh): 1,
            }),
            SceneWrapper(),
            RandomSunMaker(),
            RandomCameraPlacer((1024, 512)),
            YafaraySaver(),
            'process_yafaray'
        ): 'mazehill'
    })
    builders.update({
        PipelineBuilder(
            FilledCubicGenerator(20),
            Mesher2D(wall=0.5),
            Choice({
                Warper2D(noise.pnoise2, (noise_amount,), noise_scale/5, 5, (noise_x, noise_y)): 1,
                (lambda mesh: mesh): 0,
            }),
            ObjSaver(),
            'process_obj'
        ): 'objtest'
    })
    builders.update({
        PipelineBuilder(
            FilledCubicGenerator(50, 25, chambers=Choice({
                tuple([(random.randrange(3, 15),)
                  for _ in range(random.randrange(15))]): 10,
                tuple([(7,)] * random.randrange(15)): 5,
            })),
            ImageLineIllustrator(
                8, 2,
                features=args.emojis),
            ImageSaver(),
            'tweet_image'
        ): 'emojis'
    })
    builders.update({
        PipelineBuilder(
            FilledCubicGenerator(50, 50, chambers=[(7,)] * 10),
            # Choice({
            #     tuple([(random.randrange(3, 15),)
            #       for _ in range(random.randrange(15))]): 10,
            #     tuple([(7,)] * random.randrange(15)): 5,
            # })),
            Mesher2D(wall=0.5,
                     features=MeshFeatures(
                         '/users/kcsaff/Downloads/bunny.obj'
                     )),
            SceneWrapper(),
            RandomSunMaker(),
            RandomCameraPlacer((1024, 512)),
            YafaraySaver(),
            'process_yafaray'
        ): 'ofeatures'
    })
    builders.update({
        PipelineBuilder(
            FilledCubicGenerator(70),
            MultiMesher((
                Mesher2D(wall=0.25, height=1,
                    material=read_mtl(
                        '/users/kcsaff/Downloads/hedge_obj/hedge.mtl')
                         ['hedge_OUT']
                ),
                Mesher2D(wall=0.23, height=0.98,
                    material=read_mtl(
                        '/users/kcsaff/Downloads/hedge_obj/hedge.mtl')
                         ['hedge_IN']
                ),
            )),
            SceneWrapper(),
            RandomSunMaker(),
            RandomCameraPlacer((1024, 512)),
            YafaraySaver(),
            'process_yafaray'
        ): 'hedge'
    })
    builders.update({
        PipelineBuilder(
            FilledCubicGenerator(50, 50, barriers=[(7,)] * 10),
            Mesher2D(wall=random.random, density=2),
            TextSaver('sunk.pov'),
            'process_pov'
        ): 'sunk'
    })
    weights = dict(
        evil=20,
        fantasy=32,
        escher=17,
        brick=4,
        pure=3,
        bw2d=2,
        bw2dtilt=2,
        colors2d=4,
        pastels2d=10,
        boulders=15,
        simple3d=15,
        borg=15,
        borg2=10,
        mazehill=30,
        objtest=0,
        emojis=35,
        ofeatures=0,
        sunk=0,
        hedge=0,
    )
    processor = Processor(
        builders=Choice.of(builders).weighting(Choice.DEFAULT, weights),
        default_status=LostTextWriter().write,
        args=args
    )

    if args.autofollow:
        processor.autofollow()
    else:
        processor.start()

