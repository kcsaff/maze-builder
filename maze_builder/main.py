import argparse
import os.path
from .processor import Processor
import sys
from collections import namedtuple
import shutil
import random


POVRAY_INI = 'povray.ini'


Settings = namedtuple(
    'Settings',
    ['config', 'verbose', 'keys', 'pov', 'ini', 'include_path', 'magick', 'builder', 'tweet']
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
    '--pov', '-p', type=str,
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
    from maze_builder.cubics.builders import ImageBuilder, CubicPovBuilder
    from maze_builder.cubics.illustrators import CubicTemplateIllustrator
    from maze_builder.lost_text.writers import LostTextWriter

    processor = Processor({
        CastleBuilder('evil', TemplateIllustrator('evil.pov.jinja2')): 31,
        CastleBuilder('fantasy', TemplateIllustrator('fantasy.pov.jinja2')): 38,
        CastleBuilder('escher', TemplateIllustrator('escher.pov.jinja2')): 20,
        CastleBuilder('brick', TemplateIllustrator('brick.pov.jinja2')): 4,
        CastleBuilder('pure', TemplateIllustrator('pure.pov.jinja2')): 3,
        ImageBuilder('bw2d', 506, 253): 12,
        CubicPovBuilder('boulders', CubicTemplateIllustrator('boulders.pov.jinja2'), 50): 25,
    },
        default_status=LostTextWriter().write,
        args=args
    )

    processor.start()

