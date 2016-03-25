import random
import collections
import math
from maze_builder.sewer import Choice


def weighted_choice(choices):
    return Choice(choices)()


def hemisphere(radius=1, minz=None, maxz=None):
    if minz is None:
        minz = -radius
    if maxz is None:
        maxz = +radius
    z = minz + (maxz - minz) * random.random()
    theta = random.random()*2*math.pi

    root = math.sqrt(1-(z/radius)**2)
    x = radius * math.cos(theta) * root
    y = radius * math.sin(theta) * root

    return x, y, z

