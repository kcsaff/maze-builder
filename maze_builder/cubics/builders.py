import random
from maze_builder.random2 import weighted_choice
from maze_builder.util import timed
from .cubic import Cubic
from .illustrators import *


POV_FILENAME = 'out.pov'


PNG_FILENAME = 'out.png'


class UnicodeBuilder(object):
    def __init__(self, name, width, height=None, illustrator=UnicodeFullBlockIllustrator()):
        self.name = name
        self.width = width
        self.height = height or width
        self.illustrator = illustrator

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        with timed(verbose > 0, 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maze = Cubic(
            ).prepare(self.width, self.height, 1).fill(
            ).request_feature(1, 1
            ).request_feature(1, 1
            )

        with timed(verbose > 0, 'Writing maze...', 'Maze written in {0:.3f}s'):
            data = self.illustrator.draw(maze)
            print(len(data))
            print(data)

        if processor:
            processor.tweet(status=data)

        return data


class ImageBuilder(object):
    def __init__(self, name, width, height=None, illustrator=ImageBlockIllustrator()):
        self.name = name
        self.width = width
        self.height = height
        self.illustrator = illustrator

    def build(self, processor, verbose=0, filename=PNG_FILENAME):
        # Generate maze

        with timed(verbose > 0, 'Generating maze image...', 'Maze image generated in {0:.3f}s'):
            maze = Cubic().prepare((self.width-1)//2, (self.height-1)//2).fill()

        with timed(verbose > 0, 'Writing maze image...', 'Maze image written in {0:.3f}s'):
            image = self.illustrator.draw(maze)
            image.save(filename)

        if processor:
            processor.tweet(filename=filename)


class SatelliteBuilder(object):

    def __init__(self, name):
        self.name = name
        self.illustrator = TemplateIllustrator()

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        with timed(verbose > 0, 'Generating satellite...', 'Satellite generated in {0:.3f}s'):

            weights = {
                0: 1,
                1: 16,
                2: 8,
                3: 2
            }

            satellite = Cubic().seed(150, x=lambda: weighted_choice(weights))

        with timed(verbose > 0, 'Writing satellite...', 'Satellite written in {0:.3f}s'):

            data = self.illustrator.draw(satellite)
            with open(filename, 'w') as f:
                f.write(data)

        if processor:
            processor.process_pov(filename)
