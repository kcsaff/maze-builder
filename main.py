from castles.castle import CastleOneLevel, CastleTwoLevel
from castles.illustrators import SimpleSurfaceIllustrator, SimpleTemplateIllustrator
from castles.faces import Surface
from castles.obj import write_obj
import time

castle = CastleTwoLevel(150, 150, tower_density=0.03)


# illustrator = SimpleSurfaceIllustrator(Surface.box(1.2, 0.2, 0.5).translate((-0.1, -0.1, 0)))
#
# castle.draw(illustrator)
# with open('out.obj', 'w') as f:
#     write_obj(illustrator.make(), f)


illustrator = SimpleTemplateIllustrator('escher.pov.jinja2')

castle.draw(illustrator)
with open('out.pov', 'w') as f:
    f.write(illustrator.make())
