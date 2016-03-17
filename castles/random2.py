import random


def weighted_choice(choices, weights):
    # http://stackoverflow.com/a/17011134/1115497
    total = sum(weights)
    threshold = random.uniform(0, total)
    for choice, weight in zip(choices, weights):
        total -= weight
        if total < threshold:
            return choice
