from .features import *
from .castle import *
from maze_builder.util import timed, is_verbose


POV_FILENAME = 'out.pov'


class CastleBuilder(object):
    def __init__(self, illustrator, features=None, castle_class=CastleTwoLevel):
        self.illustrator = illustrator
        self.castle_class = castle_class
        if features is None:
            features = [
                # Keep in order from largest to smallest for best coverage
                Courtyards(0.012*4*random.random()*random.random()),
                Towers(0.007*4*random.random()*random.random()),
                Spires(0.01*4*random.random()*random.random()),
                Stairs(0.05*4*random.random()*random.random())
            ]
        self.features = features

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        with timed(is_verbose(1), 'Generating castle...', 'Castle generated in {0:.3f}s'):
            castle = self.castle_class(
                150, 150, verbose=verbose,
                feature_factories=self.features
            )

        with timed(is_verbose(1), 'Writing castle...', 'Castle written in {0:.3f}s'):
            castle.draw(self.illustrator)
            with open(filename, 'w') as f:
                f.write(self.illustrator.make())
            self.illustrator.reset()  # TODO: get rid of state here!

        if processor:
            processor.process_pov(filename)
