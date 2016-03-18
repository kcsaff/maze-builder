import argparse
import os.path
from .processor import Processor
import sys
from collections import namedtuple


POVRAY_INI = 'povray.ini'


Settings = namedtuple(
    'Settings',
    ['config', 'verbose', 'keys', 'pov', 'ini', 'include_path', 'magick', 'tweet']
)


defaults = Settings(
    config=None,
    verbose=0,
    keys=None,
    pov='povray',  # This is correct on Linux anyway
    ini=None,
    include_path=None,
    magick='convert',  # Generally correct
    tweet=False,  # Misleading, change this
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


def main(args=None):
    # Rigamarole of loading args from config (if any) & setting as defaults

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

    from maze_builder.castles.builder import CastleBuilder
    Processor(CastleBuilder(), args or parser.parse_args()).start()


