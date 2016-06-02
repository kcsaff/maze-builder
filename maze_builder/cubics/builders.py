from maze_builder.util import timed, is_verbose
from .cubic import Cubic
from .illustrators.imaging import *
from .illustrators.unicode import *
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

        with timed(is_verbose(1), 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maze = Cubic(
            ).prepare(self.width, self.height, 1).fill(
            ).request_feature(1, 1
            ).request_feature(1, 1
            )

        with timed(is_verbose(1), 'Writing maze...', 'Maze written in {0:.3f}s'):
            data = self.illustrator.draw(maze)
            print(len(data))
            print(data)

        if processor:
            processor.tweet(status=data)

        return data


class ImageBuilder(object):
    def __init__(self, width, height=None, illustrator=ImageBlockIllustrator()):
        self.width = width
        self.height = height or width
        self.illustrator = illustrator

    def build(self, processor, verbose=0, filename=PNG_FILENAME):
        # Generate maze

        with timed(is_verbose(1), 'Generating maze image...', 'Maze image generated in {0:.3f}s'):
            maze = Cubic().prepare((self.width-1)//2, (self.height-1)//2).fill()

        with timed(is_verbose(1), 'Writing maze image...', 'Maze image written in {0:.3f}s'):
            image = self.illustrator.draw(maze)
            image.save(filename)

        if processor:
            processor.tweet(filename=filename)


class ImageBuilderCombined(object):
    def __init__(self, width, height, illustrators, fun=ImageChops.multiply):
        self.width = width
        self.height = height
        self.illustrators = illustrators
        if isinstance(fun, str):
            fun = getattr(ImageChops, fun)
        self.fun = fun

    def build(self, processor, verbose=0, filename=PNG_FILENAME):
        # Generate maze
        with timed(is_verbose(1), 'Generating mazes...', 'All mazes generated in {0:.3f}s'):
            mazes = list()
            for i in range(len(self.illustrators)):
                with timed(is_verbose(2), 'Generating maze #{}...'.format(i+1), 'Maze generated in {0:.3f}s'):
                    mazes.append(Cubic().prepare((self.width-1)//2, (self.height-1)//2).fill())

        with timed(is_verbose(1), 'Combining maze images...', 'Maze images combined in {0:.3f}s'):
            images = [ill.draw(maze) for ill, maze in zip(self.illustrators, mazes)]
            image = images[0]
            for multiplier in images[1:]:
                image = self.fun(image, multiplier)
            image.save(filename)

        if processor:
            processor.tweet(filename=filename)


class CubicPovBuilder(object):
    def __init__(self, illustrator, x, y=None, z=1):
        self.illustrator = illustrator
        self.x, self.y, self.z = x, (y or x), z

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        with timed(is_verbose(1), 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maze = Cubic().prepare(
                self.x, self.y, self.z,
                origin=(-(self.x//2), -(self.y//2), -(self.z//2))
            ).fill()

        with timed(is_verbose(1), 'Writing maze...', 'Maze written in {0:.3f}s'):
            data = self.illustrator.draw(maze)
            with open(filename, 'w') as f:
                f.write(data)

        if processor:
            processor.process_pov(filename)


class SeededPovBuilder(object):
    def __init__(self, illustrator, attempts=3000):
        self.illustrator = illustrator
        self.attempts = attempts

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        with timed(is_verbose(1), 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maxx = random.randint(1, 3)
            maxy = random.randint(1, 3)
            maxz = random.randint(1, 3)
            maze = Cubic().seed(
                self.attempts,
                x=lambda: random.randint(1, maxx),
                y=lambda: random.randint(1, maxy),
                z=lambda: random.randint(1, maxz),
            )

        with timed(is_verbose(1), 'Writing maze...', 'Maze written in {0:.3f}s'):
            data = self.illustrator.draw(maze)
            with open(filename, 'w') as f:
                f.write(data)

        if processor:
            processor.process_pov(filename)


class FilledCubicGenerator(object):
    def __init__(self, x, y=None, z=1):
        self.x = x
        self.y = y or x
        self.z = z

    def __call__(self, verbose=1):
        with timed(is_verbose(1), 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maze = Cubic().prepare(
                self.x, self.y, self.z,
                origin=(-self.x//2, -self.y//2, -self.z//2)
            ).fill()
            return maze
