import random
import subprocess
import os.path
from .util import timed
from .random2 import weighted_choice


TWITTER_FILESIZE_LIMIT = 2999000 # About 3 Meg, we round down
NEW_FILESIZE_LIMIT = '1999kb'
OUT_FILENAME = 'out.png'
JPG_FILENAME = 'out{}.jpg'


class Processor(object):
    def __init__(self, builders, default_status=None, args=None):
        self.args = args
        self.verbose = args.verbose
        self.default_status = default_status
        self.builders = builders
        self.builders_by_name = {
            builder.name: builder
            for builder in builders
            if getattr(builder, 'name', None)
        }

    def start(self):
        if self.args.tweet:
            self.tweet(filename=OUT_FILENAME)
        elif self.args.builder:
            self.builders_by_name[self.args.builder].build(self, self.verbose)
        else:
            weighted_choice(self.builders).build(self, self.verbose)

    def process_pov(self, filename):
        if not self.args or not self.args.pov:
            if self.verbose > 0:
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

        with timed(self.verbose, 'Rendering maze...', 'Maze rendered in {0:.3f}s'):
            subprocess.check_call(pov_args)

        if self.args.keys:
            self.tweet(filename=OUT_FILENAME)

    def tweet(self, status=None, filename=None):
        if status is None and self.default_status is not None:
            status = self.default_status() if callable(self.default_status) else self.default_status

        if not self.args or not self.args.keys:
            if self.verbose > 0:
                print('No twitter keys registered, pipeline stopping')
            return

        from maze_builder.bot import bot

        twitter = bot(self.args.keys)

        if status:
            kwargs = dict(status=status)
        else:
            kwargs = dict()

        if filename:
            filename = self._resize(filename)

            with timed(
                self.verbose > 0,
                'Updating twitter status ({}kb)...'.format(os.path.getsize(filename) // 1024),
                'Updated status in {0:.3f}s'
            ):
                twitter.update_with_media(filename, **kwargs)
        elif status:
            twitter.update_status(**kwargs)
        else:
            raise RuntimeError('Tweet requires status or filename')

    def _resize(self, filename):
        if not self.args or not self.args.magick:
            raise RuntimeError('No ImageMagick handler registered & it\'s required to resize! Pipeline stopping')

        file_size = os.path.getsize(filename)

        attempt = 0
        while file_size > TWITTER_FILESIZE_LIMIT and attempt < 5:
            with timed(self.verbose > 0, 'Needs more jpeg...', 'Resized image in {0:.3f}s'):
                new_filename = JPG_FILENAME.format(attempt)
                call_args = [
                    self.args.magick, filename,
                    '-define', 'jpeg:extent={}'.format(NEW_FILESIZE_LIMIT),
                ]
                if attempt > 0:
                    call_args.extend(['-scale', '70%'])
                call_args.append(new_filename)
                subprocess.check_call(call_args)
                filename = new_filename
                file_size = os.path.getsize(filename)

        return filename


def read_ini_sections(filename):
    if not os.path.exists(filename) and not filename.lower().endswith('.ini'):
        filename += '.ini'
    with open(filename, 'r') as f:
        data = f.read()
    import re
    return re.findall('^\[(\w+)\]', data, re.MULTILINE)

