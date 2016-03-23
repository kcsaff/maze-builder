from maze_builder.util import timed
from .cubic import Cubic
from .illustrators.imaging import *
from .illustrators.unicode import *
from PIL import ImageChops


POV_FILENAME = 'out.pov'


OBJ_FILENAME = 'out.obj'


PNG_FILENAME = 'out.png'


YAFARAY_FILENAME = 'out.yafaray.xml'


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
        with timed(verbose > 0, 'Generating mazes...', 'All mazes generated in {0:.3f}s'):
            mazes = list()
            for i in range(len(self.illustrators)):
                with timed(verbose > 1, 'Generating maze #{}...'.format(i+1), 'Maze generated in {0:.3f}s'):
                    mazes.append(Cubic().prepare((self.width-1)//2, (self.height-1)//2).fill())

        with timed(verbose > 0, 'Combining maze images...', 'Maze images combined in {0:.3f}s'):
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

        with timed(verbose > 0, 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maze = Cubic().prepare(
                self.x, self.y, self.z,
                origin=(-(self.x//2), -(self.y//2), -(self.z//2))
            ).fill()

        with timed(verbose > 0, 'Writing maze...', 'Maze written in {0:.3f}s'):
            data = self.illustrator.draw(maze)
            with open(filename, 'w') as f:
                f.write(data)

        if processor:
            processor.process_pov(filename)


class SeededPovBuilder(object):
    def __init__(self, name, illustrator, attempts=3000):
        self.name = name
        self.illustrator = illustrator
        self.attempts = attempts

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        with timed(verbose > 0, 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maxx = random.randint(1, 3)
            maxy = random.randint(1, 3)
            maxz = random.randint(1, 3)
            maze = Cubic().seed(
                self.attempts,
                x=lambda: random.randint(1, maxx),
                y=lambda: random.randint(1, maxy),
                z=lambda: random.randint(1, maxz),
            )

        with timed(verbose > 0, 'Writing maze...', 'Maze written in {0:.3f}s'):
            data = self.illustrator.draw(maze)
            with open(filename, 'w') as f:
                f.write(data)

        if processor:
            processor.process_pov(filename)


class CubicObjBuilder(object):
    def __init__(self, name, illustrator, x, y=None, z=1):
        self.name = name
        self.illustrator = illustrator
        self.x, self.y, self.z = x, (y or x), z

    def build(self, processor, verbose=0, filename=OBJ_FILENAME):
        # Generate maze

        with timed(verbose > 0, 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maze = Cubic().prepare(
                self.x, self.y, self.z,
                origin=(-self.x/2, -self.y/2, -self.z/2)
            ).fill()

        with timed(verbose > 0, 'Writing maze...', 'Maze written in {0:.3f}s'):
            self.illustrator.draw(maze, filename)

        if processor:
            processor.process_obj(filename)


class CubicYafarayBuilder(object):
    def __init__(self, name, illustrator, x, y=None, z=1):
        self.name = name
        self.illustrator = illustrator
        self.x, self.y, self.z = x, (y or x), z

    def build(self, processor, verbose=0, filename=YAFARAY_FILENAME):
        # Generate maze

        with timed(verbose > 0, 'Generating maze...', 'Maze generated in {0:.3f}s'):
            maze = Cubic().prepare(
                self.x, self.y, self.z,
                origin=(-self.x/2, -self.y/2, -self.z/2)
            ).fill()

        with timed(verbose > 0, 'Writing maze...', 'Maze written in {0:.3f}s'):
            self.illustrator.draw(maze, filename)

        if processor:
            processor.process_yafaray(filename)
