import time
from .features import *
from .castle import *
from .illustrators import WeightedTemplateIllustrator


clock = time.perf_counter


POV_FILENAME = 'out.pov'


class CastleBuilder(object):
    def __init__(self, features=None, illustrator=None, castle_class=CastleTwoLevel):
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
        if illustrator is None:
            illustrator = WeightedTemplateIllustrator({
                    'evil.pov.jinja2':    31,
                    'fantasy.pov.jinja2': 38,
                    'escher.pov.jinja2':  25,
                    'brick.pov.jinja2':    4,
                    'pure.pov.jinja2':     2,
            })
        self.illustrator = illustrator
        print ((illustrator, self.illustrator))

    def build(self, processor, verbose=0, filename=POV_FILENAME):
        # Generate maze

        started = clock()
        if verbose:
            print('Generating castle...')

        castle = self.castle_class(
            100, 100, verbose=verbose,
            feature_factories=self.features
        )

        if verbose:
            elapsed = clock() - started
            print('Castle generated in {0:.3f}s'.format(elapsed))

        started = clock()
        if verbose:
            print('Writing castle...')

        castle.draw(self.illustrator)
        with open(filename, 'w') as f:
            f.write(self.illustrator.make())
        self.illustrator.reset()  # TODO: get rid of state here?

        if verbose:
            elapsed = clock() - started
            print('Castle written in {0:.3f}s'.format(elapsed))

        if processor:
            processor.process_pov(filename)
