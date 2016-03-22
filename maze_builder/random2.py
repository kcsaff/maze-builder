import random
import collections


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

    def __call__(self, call=False):
        if self.total is None:
            weights = [weight() if callable(weight) else weight for weight in self.weights]
            total = sum(weights)
        else:
            weights, total = self.weights, self.total

        # http://stackoverflow.com/a/17011134/1115497
        threshold = random.uniform(0, total)
        for choice, weight in zip(self.choices, weights):
            total -= weight
            if total < threshold:
                if call and callable(choice):
                    return choice()
                else:
                    return choice


def weighted_choice(choices, weights=None):
    return WeightedChoice(choices, weights)()
