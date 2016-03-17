from castles.castle import CastleOneLevel, CastleTwoLevel
from castles.illustrators import SimpleSurfaceIllustrator, SimpleTemplateIllustrator
import argparse
import subprocess
import random
from castles.faces import Surface
from castles.obj import write_obj
import time
from castles.random2 import weighted_choice


clock = time.perf_counter


# illustrator = SimpleSurfaceIllustrator(Surface.box(1.2, 0.2, 0.5).translate((-0.1, -0.1, 0)))
#
# castle.draw(illustrator)
# with open('out.obj', 'w') as f:
#     write_obj(illustrator.make(), f)

POV_FILENAME = 'out.pov'
OUT_FILENAME = 'out.png'


parser = argparse.ArgumentParser('Forgotten Castles Bot')
parser.add_argument(
    '--verbose', '-v', action='count'
)
parser.add_argument(
    '--keys', '-k', type=str,
    help='Keys file needed to post to Twitter',
    default='keys.txt'
)
parser.add_argument(
    '--pov', '-p', type=str,
    help='Path to POV-Ray executable',
    default='/Users/kcsaff/Downloads/PovrayCommandLineMacV2/Povray37UnofficialMacCmd'
)
parser.add_argument(
    '--ini', '-i', type=str,
    help='INI file to pass to POV-Ray -- a random choice will be made for comma-separated filenames',
    default='povray,povray[p720],povray[p1080],povray[iphone4]'
)
parser.add_argument(
    '--include-path', '-I', type=str,
    help='POV-Ray include path(s), comma-separated',
    default='/Users/kcsaff/Downloads/PovrayCommandLineMacV2/include'
)

args = parser.parse_args()
verbose = args.verbose

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
        'fantasy.pov.jinja2': 50,
        'escher.pov.jinja2':  40,
        'brick.pov.jinja2':    7,
        'pure.pov.jinja2':     3,
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
    pov_args = [
        args.pov,
    ]
    if args.ini:
        pov_args.append(random.choice(args.ini.split(',')).strip())
    if args.include_path:
        pov_args.extend('+L{}'.format(path.strip()) for path in args.include_path.split(','))
    pov_args.extend([
        '+I{}'.format(POV_FILENAME),
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
        from castles.bot import bot

        started = clock()
        if verbose:
            print('Updating twitter status...')

        bot(args.keys).update_with_media(OUT_FILENAME)

        if verbose:
            elapsed = clock() - started
            print('Updated status in {0:.3f}s'.format(elapsed))

