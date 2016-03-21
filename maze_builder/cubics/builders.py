import random
from maze_builder.random2 import weighted_choice
from maze_builder.util import timed
from .cubic import Cubic
from .illustrators import *
from numbers import Number
from PIL import ImageChops


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


class ImageBuilderCombined(object):
    def __init__(self, name, width, height, illustrators, fun=ImageChops.multiply):
        self.name = name
        self.width = width
        self.height = height
        self.illustrators = illustrators
        if isinstance(fun, str):
            fun = getattr(ImageChops, fun)
        self.fun = fun

    def build(self, processor, verbose=0, filename=PNG_FILENAME):
        # Generate maze
        with timed(verbose > 0, 'Generating mazes...', 'Maze image generated in {0:.3f}s'):
            mazes = [Cubic().prepare((self.width-1)//2, (self.height-1)//2).fill() for ill in self.illustrators]

        with timed(verbose > 0, 'Writing maze images...', 'Maze image written in {0:.3f}s'):
            images = [ill.draw(maze) for ill, maze in zip(self.illustrators, mazes)]
            image = images[0]
            for multiplier in images[1:]:
                image = self.fun(image, multiplier)
            image.save(filename)

        if processor:
            processor.tweet(filename=filename)


class CubicPovBuilder(object):
    def __init__(self, name, illustrator, x, y=None, z=1):
        self.name = name
        self.illustrator = illustrator
        self.x, self.y, self.z = x, (y or x), z

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        with timed(verbose > 0, 'Generating maze...', 'Satellite generated in {0:.3f}s'):
            maze = Cubic().prepare(
                self.x, self.y, self.z,
                origin=(-self.x/2, -self.y/2, -self.z/2)
            ).fill()

        with timed(verbose > 0, 'Writing maze...', 'Satellite written in {0:.3f}s'):
            data = self.illustrator.draw(maze)
            with open(filename, 'w') as f:
                f.write(data)

        if processor:
            processor.process_pov(filename)
