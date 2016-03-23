import argparse
import os.path
from .processor import Processor
import sys
from collections import namedtuple
import shutil
import random
import math
import noise


POVRAY_INI = 'povray.ini'


Settings = namedtuple(
    'Settings',
    ['config', 'verbose', 'keys',
     'pov', 'ini', 'include_path',
     'magick',
     'builder', 'tweet',
     'yafaray', 'yafaray_plugins',
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
    builder=None,
    tweet=False,  # Misleading, change this
    yafaray=None,
    yafaray_plugins=None,
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
    '--builder', '-b', type=str,
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

    from maze_builder.castles.builder import CastleBuilder
    from maze_builder.castles.illustrators import TemplateIllustrator
    from maze_builder.cubics.builders import ImageBuilder, CubicPovBuilder, ImageBuilderCombined, SeededPovBuilder, \
        CubicObjBuilder, CubicYafarayBuilder
    from maze_builder.cubics.illustrators.template import CubicTemplateIllustrator
    from maze_builder.cubics.illustrators.imaging import ImageBlockIllustratorZoomed
    from maze_builder.cubics.illustrators.mesh import ObjIllustrator, YafarayIllustrator
    from maze_builder.lost_text.writers import LostTextWriter

    builders = {
        CastleBuilder('evil', TemplateIllustrator('evil.pov.jinja2')): 31,
        CastleBuilder('fantasy', TemplateIllustrator('fantasy.pov.jinja2')): 32,
        CastleBuilder('escher', TemplateIllustrator('escher.pov.jinja2')): 17,
        CastleBuilder('brick', TemplateIllustrator('brick.pov.jinja2')): 4,
        CastleBuilder('pure', TemplateIllustrator('pure.pov.jinja2')): 3,
        ImageBuilder('bw2d', 506, 253): 3,
        ImageBuilder('bw2dtilt', 506, 253, illustrator=ImageBlockIllustratorZoomed()): 2,
        ImageBuilderCombined('colors2d', 512, 512, (
            ImageBlockIllustratorZoomed(hall_colors=[(255,0,0)], size=(506, 253)),
            ImageBlockIllustratorZoomed(hall_colors=[(0,255,0)], size=(506, 253)),
            ImageBlockIllustratorZoomed(hall_colors=[(0,0,255)], size=(506, 253)),
        ), 'add'): 5,
        ImageBuilderCombined('pastels2d', 512, 512, (
            ImageBlockIllustratorZoomed(wall_colors=[tuple(int(256*(1-random.random()**2)) for _ in range(3))], size=(506, 253)),
            ImageBlockIllustratorZoomed(wall_colors=[tuple(int(256*(1-random.random()**2)) for _ in range(3))], size=(506, 253)),
            ImageBlockIllustratorZoomed(wall_colors=[tuple(int(256*(1-random.random()**2)) for _ in range(3))], size=(506, 253)),
        ), 'multiply'): 25,
        CubicPovBuilder('boulders', CubicTemplateIllustrator('boulders.pov.jinja2'), 50): 20,
        CubicPovBuilder('simple3d', CubicTemplateIllustrator('simple.pov.jinja2'), 50): 30,
        CubicPovBuilder('borg', CubicTemplateIllustrator('borg.pov.jinja2'), 8, 8, 8): 15,
        SeededPovBuilder('borg2', CubicTemplateIllustrator('borg.pov.jinja2')): 10,
    }
    noise_amount = 10
    noise_scale = 2**(noise_amount-3)
    noise_x = 1000 * random.random()
    noise_y = 1000 * random.random()
    builders.update({
        CubicYafarayBuilder(
            'mazehill',
            YafarayIllustrator(
                'simple.yafaray.xml',
                width=0.5,
                height=(lambda x,y: 0.75+noise_scale*noise.pnoise2(noise_x+x/5/noise_scale, noise_y+y/5/noise_scale, noise_amount)),
                depth=(lambda x,y: noise_scale*noise.pnoise2(noise_x+x/5/noise_scale, noise_y+y/5/noise_scale, noise_amount)),
                density=2, smoothing_degrees=35,
            ), 150, 150): 30,
    })
    builders.update({
        CubicObjBuilder(
            'objtest',
            ObjIllustrator(
                width=0.5,
                height=(lambda x,y: 0.75+noise_scale*noise.pnoise2(noise_x+x/5/noise_scale, noise_y+y/5/noise_scale, noise_amount)),
                depth=(lambda x,y: noise_scale*noise.pnoise2(noise_x+x/5/noise_scale, noise_y+y/5/noise_scale, noise_amount)),
                density=4, smoothing_degrees=35, enclosed=True
            ), 20, 20): 0,
    })
    processor = Processor(
        builders=builders,
        default_status=LostTextWriter().write,
        args=args
    )

    processor.start()

