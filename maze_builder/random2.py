import random
import collections
import math


class WeightedChoice(object):
    def __init__(self, choices, weights=None):
        if weights is None:
            if isinstance(choices, dict):
                choices, weights = zip(*choices.items())
            elif isinstance(choices, collections.Iterable):
                weights = [1] * len(choices)
        self.choices, self.weights = choices, weights

        if any(callable(weight) for weight in self.weights):
            self.total = None
        else:
            self.total = sum(self.weights)

    def __iter__(self):
        return iter(self.choices)

    @classmethod
    def of(self, obj):
        if isinstance(obj, WeightedChoice) or callable(obj):
            return obj
        else:
            return WeightedChoice(obj)

    def __call__(self, filter=None, call=False):
        if self.total is None or filter is not None:
            choices, weights = zip(*(
                (choice, weight() if callable(weight) else weight)
                for choice, weight in zip(self.choices, self.weights)
                if filter is None or filter(choice)
            ))
            total = sum(weights)
        else:
            choices, weights, total = self.choices, self.weights, self.total
        if len(choices) == 1:
            return choices[0]
        elif total <= 0:
            raise KeyError('No items available in WeightedChoice')

        # http://stackoverflow.com/a/17011134/1115497
        threshold = random.uniform(0, total)
        for choice, weight in zip(choices, weights):
            total -= weight
            if total < threshold:
                if call and callable(choice):
                    return choice()
                else:
                    return choice


def weighted_choice(choices, weights=None):
    return WeightedChoice(choices, weights)()


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

