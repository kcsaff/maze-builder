import random
import collections


def weighted_choice(choices, weights=None):
    if weights is None:
        if isinstance(choices, dict):
            choices, weights = zip(*choices.items())
        elif isinstance(choices, collections.Iterable):
            weights = [1] * len(choices)

    weights = [weight() if callable(weight) else weight for weight in weights]

    # http://stackoverflow.com/a/17011134/1115497
    total = sum(weights)
    threshold = random.uniform(0, total)
    for choice, weight in zip(choices, weights):
        total -= weight
        if total < threshold:
            return choice
