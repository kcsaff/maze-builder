import argparse
from .processor import Processor


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


def main(args=None):
    from maze_builder.castles.builder import CastleBuilder
    Processor(CastleBuilder(), args or parser.parse_args()).start()


