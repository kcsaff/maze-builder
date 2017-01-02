import random
import subprocess
import os.path
from .util import timed, verbosity, is_verbose
from .random2 import weighted_choice, Choice
from maze_builder.sewer import Pipeline
import itertools


TWITTER_FILESIZE_LIMIT = 2999000 # About 3 Meg, we round down
NEW_FILESIZE_LIMIT = '1999kb'
OUT_FILENAME = 'out.png'
OUT_YAFARAY = 'out', 'out.tga'
JPG_FILENAME = 'out{}.jpg'


class PipelineBuilder(object):
    def __init__(self, *steps):
        self.pipeline = Pipeline(*steps)

    def build(self, processor, verbose=0, filename=None):
        methods = {key: getattr(processor, key) for key in dir(processor) if not key.endswith('__')}
        return self.pipeline.product(verbose, methods)


class Processor(object):
    def __init__(self, builders, default_status=None, args=None):
        self.args = args
        self.verbose = args.verbose
        self.default_status = default_status
        self.builders = Choice.of(builders)
        self._twitter = None

    @property
    def twitter(self):
        if self.args.keys and self._twitter is None:
            from maze_builder.bot import bot

            self._twitter = bot(self.args.keys)
        return self._twitter

    def start(self):
        with verbosity(self.verbose):
            print(self.verbose)
            if self.args.tweet:
                self.tweet(filename=OUT_FILENAME)

            builder = self.args.builder or 'default'

            try:
                builder = self.builders(tag=builder)
            except:
                print('No builder named `{}`. Available builders are:'.format(builder))
                for name in sorted(self.builders.tags()):
                    print(' * {}'.format(name))
                raise RuntimeError('No builder named `{}`'.format(builder))
            else:
                builder.build(self, self.verbose)

    def process_obj(self, filename):
        if self.verbose > 0:
            print('No OBJ handler registered, pipeline stopping')
        return

    def process_yafaray(self, filename):
        if not self.args or not self.args.yafaray:
            if self.verbose > 0:
                print('No Yafaray XML handler registered, pipeline stopping')
            return

        yafaray = self.args.yafaray

        plugins = self.args.yafaray_plugins
        if not plugins:
            candidate = os.path.join(os.path.dirname(yafaray), 'plugins')
            if os.path.exists(candidate):
                plugins = candidate

        yafaray_args = [
            self.args.yafaray,
            #'-vl2'
        ]

        if plugins:
            yafaray_args.extend(('-pp', plugins))

        yafaray_args.extend((filename, OUT_YAFARAY[0]))

        with timed(is_verbose(1), 'Yafaray is rendering maze...', 'Maze rendered in {0:.3f}s'):
            subprocess.check_call(yafaray_args)

        filename = self._convert(OUT_YAFARAY[-1])

        if self.args.keys:
            self.tweet(filename=filename)

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

        with timed(is_verbose(1), 'POV-Ray is rendering maze...', 'Maze rendered in {0:.3f}s'):
            subprocess.check_call(pov_args)

        if self.args.keys:
            self.tweet(filename=OUT_FILENAME)

    def tweet_image(self, filename):
        return self.tweet(filename=filename)

    def autofollow(self):
        import tweepy
        followers = set(tweepy.Cursor(self.twitter.followers_ids).items())
        friends = set(tweepy.Cursor(self.twitter.friends_ids).items())
        print(followers)
        print(friends)

        print('Need to follow: {}'.format(followers - friends))
        print('Need to unfollow: {}'.format(friends - followers))

        for user_id in followers - friends:
            self.twitter.create_friendship(user_id)

        for user_id in friends - followers:
            self.twitter.destroy_friendship(user_id)

    def tweet(self, status=None, filename=None):
        if status is None and self.default_status is not None:
            status = self.default_status() if callable(self.default_status) else self.default_status

        if not self.args or not self.args.keys:
            if self.verbose > 0:
                print('No twitter keys registered, pipeline stopping')
            return

        if status:
            kwargs = dict(status=status)
        else:
            kwargs = dict()

        if filename:
            filename = self._resize(filename)

            with timed(
                is_verbose(1),
                'Updating twitter status ({}kb)...'.format(os.path.getsize(filename) // 1024),
                'Updated status in {0:.3f}s'
            ):
                self.twitter.update_with_media(filename, **kwargs)
        elif status:
            self.twitter.update_status(**kwargs)
        else:
            raise RuntimeError('Tweet requires status or filename')

    def _convert(self, filename, outname=OUT_FILENAME):
        if filename == outname:
            return outname

        if not self.args or not self.args.magick:
            raise RuntimeError('No ImageMagick handler registered & it\'s required to convert! Pipeline stopping')

        with timed(is_verbose(1), 'Converting image...', 'Converted image in {0:.3f}s'):
            call_args = [
                self.args.magick, filename, outname
            ]
            subprocess.check_call(call_args)

        return outname

    def _resize(self, filename):
        if not self.args or not self.args.magick:
            raise RuntimeError('No ImageMagick handler registered & it\'s required to resize! Pipeline stopping')

        file_size = os.path.getsize(filename)

        attempt = 0
        while file_size > TWITTER_FILESIZE_LIMIT and attempt < 5:
            with timed(is_verbose(1), 'Needs more jpeg...', 'Resized image in {0:.3f}s'):
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

