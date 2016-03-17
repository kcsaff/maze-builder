from castles.castle import CastleOneLevel, CastleTwoLevel
from castles.illustrators import SimpleSurfaceIllustrator, SimpleTemplateIllustrator
import argparse
import subprocess
import random
import time
import os.path
from castles.random2 import weighted_choice


TWITTER_FILESIZE_LIMIT = 2800000 # About 3 Meg, we round down
NEW_FILESIZE_LIMIT = '999kb'


clock = time.perf_counter


# illustrator = SimpleSurfaceIllustrator(Surface.box(1.2, 0.2, 0.5).translate((-0.1, -0.1, 0)))
#
# castle.draw(illustrator)
# with open('out.obj', 'w') as f:
#     write_obj(illustrator.make(), f)

POV_FILENAME = 'out.pov'
OUT_FILENAME = 'out.png'
JPG_FILENAME = 'out{}.jpg'


parser = argparse.ArgumentParser('Forgotten Castles Bot')
parser.add_argument(
    '--verbose', '-v', action='count',
    default=0,
    help='More v\'s, more verbose (up to 4)'
)
parser.add_argument(
    '--keys', '-k', type=str,
    help='Keys file needed to post to Twitter',
    default='keys.txt'
)
parser.add_argument(
    '--pov', '-p', type=str,
    help='Path to POV-Ray executable',
    default=None #'/Users/kcsaff/Downloads/PovrayCommandLineMacV2/Povray37UnofficialMacCmd'
)
parser.add_argument(
    '--ini', '-i', type=str,
    help='INI file to pass to POV-Ray -- a random choice will be made for comma-separated filenames',
    default=None #'povray,povray[p720],povray[p1080],povray[iphone4]'
)
parser.add_argument(
    '--include-path', '-I', type=str,
    help='POV-Ray include path(s), comma-separated',
    default=None #'/Users/kcsaff/Downloads/PovrayCommandLineMacV2/include'
)
parser.add_argument(
    '--magick', '-M', type=str,
    help='ImageMagick command line tool',
    default='convert'
)
parser.add_argument(
    '--tweet', '-T',
    action='store_true', default=False,
    help='Tweet already rendered image',
)


def render(args=None, filename=POV_FILENAME):
    args = args or parser.parse_args()
    verbose = args.verbose

    pov_args = [
        args.pov,
    ]
    if args.ini:
        pov_args.append(random.choice(args.ini.split(',')).strip())
    if args.include_path:
        pov_args.extend('+L{}'.format(path.strip()) for path in args.include_path.split(','))
    pov_args.extend([
        '+I{}'.format(filename),
        '+O{}'.format(OUT_FILENAME),
        '-P', '-D', '-V', '+FN8'
    ])

    started = clock()
    if verbose:
        print('Rendering maze...')

    subprocess.check_call(pov_args)

    if verbose:
        elapsed = clock() - started
        print('Maze rendered in {0:.3f}s'.format(elapsed))

    if args.keys:
        tweet(args, OUT_FILENAME)


def tweet(args=None, filename=OUT_FILENAME):
    args = args or parser.parse_args()
    verbose = args.verbose

    filesize = os.path.getsize(filename)
    attempt=0
    while filesize > TWITTER_FILESIZE_LIMIT and attempt < 5:
        if verbose:
            print('Needs more jpeg...')

        new_filename = JPG_FILENAME.format(attempt)
        subprocess.check_call([
            args.magick, filename,
            '-define', 'jpeg:extent={}'.format(NEW_FILESIZE_LIMIT),
            '-scale 70%',
            new_filename
        ])
        filename = new_filename
        filesize = os.path.getsize(filename)

    from castles.bot import bot

    started = clock()
    if verbose:
        print('Updating twitter status ({}kb)...'.format(filesize // 1024))

    bot(args.keys).update_with_media(filename)

    if verbose:
        elapsed = clock() - started
        print('Updated status in {0:.3f}s'.format(elapsed))


def main(args=None):
    args = args or parser.parse_args()
    verbose = args.verbose

    if args.tweet:
        tweet(args)
        return

    # Generate maze

    started = clock()
    if verbose:
        print('Generating maze...')

    castle = CastleTwoLevel(
        100, 100, verbose=args.verbose,
        spire_density=0.01*4*random.random()*random.random(),
        courtyard_density=0.012*4*random.random()*random.random(),
        tower_density=0.007*4*random.random()*random.random(),
        stair_density=0.05*4*random.random()*random.random(),
    )

    if verbose:
        elapsed = clock() - started
        print('Maze generated in {0:.3f}s'.format(elapsed))

    # Write maze

    illustrator = SimpleTemplateIllustrator(
        weighted_choice(*zip(*{
            'evil.pov.jinja2':    31,
            'fantasy.pov.jinja2': 38,
            'escher.pov.jinja2':  25,
            'brick.pov.jinja2':    4,
            'pure.pov.jinja2':     2,
        }.items()))
    )

    started = clock()
    if verbose:
        print('Writing maze...')

    castle.draw(illustrator)
    with open(POV_FILENAME, 'w') as f:
        f.write(illustrator.make())

    if verbose:
        elapsed = clock() - started
        print('Maze written in {0:.3f}s'.format(elapsed))

    if args.pov:
        render(args, POV_FILENAME)

