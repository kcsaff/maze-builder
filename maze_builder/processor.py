import random
import time
import subprocess
import os.path


TWITTER_FILESIZE_LIMIT = 2800000 # About 3 Meg, we round down
NEW_FILESIZE_LIMIT = '1999kb'
OUT_FILENAME = 'out.png'
JPG_FILENAME = 'out{}.jpg'


clock = time.perf_counter


class Processor(object):
    def __init__(self, builder, args=None):
        self.args = args
        self.verbose = args.verbose
        self.builder = builder

    def start(self):
        if self.args.tweet:
            self.tweet()
        else:
            self.builder.build(self, self.verbose)

    def process_pov(self, filename):
        if not self.args or not self.args.pov:
            if self.verbose >= 2:
                print('No POV handler registered, pipeline stopping')
            return

        pov_args = [
            self.args.pov,
        ]
        if self.args.ini:
            ini = random.choice(self.args.ini.split(',')).strip()
            if ini.endswith('[]'):
                section = random.choice(read_ini_sections(ini[:-2]))
                ini = '{}[{}]'.format(ini[:-2], section)
            pov_args.append(ini)
        else:
            # Default size
            pov_args.extend(['+W1024', '+H768'])
        if self.args.include_path:
            pov_args.extend('+L{}'.format(path.strip()) for path in self.args.include_path.split(','))
        pov_args.extend([
            '+I{}'.format(filename),
            '+O{}'.format(OUT_FILENAME),
            '-P', '-D', '-V', '+FN8'
        ])

        started = clock()
        if self.verbose:
            print('Rendering maze...')

        subprocess.check_call(pov_args)

        if self.verbose:
            elapsed = clock() - started
            print('Maze rendered in {0:.3f}s'.format(elapsed))

        if self.args.keys:
            self.tweet(OUT_FILENAME)

    def tweet(self, filename=OUT_FILENAME):
        filesize = os.path.getsize(filename)
        attempt=0
        while filesize > TWITTER_FILESIZE_LIMIT and attempt < 5:
            if self.verbose:
                print('Needs more jpeg...')

            new_filename = JPG_FILENAME.format(attempt)
            subprocess.check_call([
                self.args.magick, filename,
                '-define', 'jpeg:extent={}'.format(NEW_FILESIZE_LIMIT),
                '-scale', '70%',
                new_filename
            ])
            filename = new_filename
            filesize = os.path.getsize(filename)

        from maze_builder.bot import bot

        started = clock()
        if self.verbose:
            print('Updating twitter status ({}kb)...'.format(filesize // 1024))

        bot(self.args.keys).update_with_media(filename)

        if self.verbose:
            elapsed = clock() - started
            print('Updated status in {0:.3f}s'.format(elapsed))


def read_ini_sections(filename):
    if not os.path.exists(filename) and not filename.lower().endswith('.ini'):
        filename += '.ini'
    with open(filename, 'r') as f:
        data = f.read()
    import re
    return re.findall('^\[(\w+)\]', data, re.MULTILINE)

