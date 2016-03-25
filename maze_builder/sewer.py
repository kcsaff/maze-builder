"""
A `Sewer` is a pipeline for mutating things.

                  _.---._
              _.-(_o___o_)
              )_.'_     _'.
            _.-( (_`---'_) )-._
          .'_.-'-._`"^"`_.-'-._'.
          /` |    __`"`__    | `\
         |   | .'`  ^:^  `'. |   |
         )'-.//      |      \\.-'(
        /   //       |       \\   \
        \   |=======.=.=======|   /
         )`-|      ( R )      |-'(
         \  \======/-\'\======/  /
          \,=(    <_/;\_|    )=,/
          /  -\      |      /-  \
          | (`-'\    |    /'-`) |
          \\_`\  '.__|__.'  /`_//
            /     /     \     \
           /    /`       `\    \
          /_,="(           )"=,_\
          )-_,="\         /"=,_-(
           \    (         )    /
            \    |       |    /
       jgs   )._ |       | _.(
         _.-'   '/       \'   '-._
        (__,'  .'         '.  ',__)
           '--`             `--'
"""

import collections
import re
import itertools
import random


def _select(obj, blessed=False):
    if blessed or isinstance(obj, Selector):
        return _select(obj())
    else:
        return obj


def _pipe(fun, value, *environment):
    fun = _select(fun)
    if fun is None:
        return value
    elif isinstance(fun, Pipeline):
        value = yield from fun(value, *environment)
    elif callable(fun):
        value = fun(value)
        received = yield value
        if received is not None:
            value = received
    else:
        for i, obj in enumerate(environment):
            if fun in obj:
                value = yield from _pipe(_select(obj[fun]), value, *environment[i:])
                break
        else:
            raise KeyError('No context contains key `{}`'.format(fun))
    return value


class Selector(object):
    def __init__(self, value=None, blessed=False):
        self.__value = value
        self.__blessed = blessed

    def __call__(self):
        if self.__blessed:
            return _select(self.__value())
        else:
            return _select(self.__value)

    @classmethod
    def of(cls, obj, blessed=False):
        if isinstance(obj, Selector):
            return obj
        elif isinstance(obj, str):
            return cls(obj)
        elif isinstance(obj, collections.Iterable):
            return Choice(obj)
        else:
            return cls(obj)

    @classmethod
    def bless(cls, obj):
        return cls.of(obj, blessed=True)


class Choice(Selector):
    def __init__(self, choices=(), **extras):
        self.choices, self.weights = self.__build_choices_and_weights(choices, **extras)
        self.__update_total()

    def update(self, choices=(), **extras):
        choices, weights = self.__build_choices_and_weights(choices, **extras)
        self.choices += choices
        self.weights += weights
        self.__update_total()

    def __call__(self, filter=None):
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
                return _select(choice)

    @classmethod
    def __build_choices_and_weights(cls, choices=(), **extras):
        if isinstance(choices, dict):
            choices = choices.items()
        elif isinstance(choices, str):
            choices = ((choices, 1),)
        elif isinstance(choices, collections.Iterable):
            choices = collections.Counter(choices).items()

        choices, weights = zip(*itertools.chain(choices, extras.items()))
        return choices, weights

    def __update_total(self):
        if any(callable(weight) for weight in self.weights):
            self.total = None
        else:
            self.total = sum(self.weights)


class MadLibs(Selector):
    __RE_PATTERN = re.compile(r'\{\s*(\w+(\s*\w+)*)\s*\}')

    def __init__(self, start, *phrasesets, **extras):
        self.__start = Selector.of(start)
        self.__phrases = dict()
        for phrases in itertools.chain(phrasesets, [extras]):
            self.__phrases.update({
                category: Selector.of(phrase)
                for category, phrase in dict(phrases).items()
            })

    def __call__(self, category=None):
        if category is None:
            replacement = _select(self.__start)
        else:
            if category is not None:
                category, *formats = category.split()
            replacement = self.__get(category)
            for format in formats:
                replacement = self.format(replacement, format)
        return self.__RE_PATTERN.sub(self.__repl_match, str(replacement))

    def format(self, value, format=None):
        formatter = self.__get(format)
        formatter = formatter.format if not callable(formatter) else formatter
        return formatter(value)

    def appending(self, text='', category=None):
        if text:
            return text + ' ' + self(category)
        else:
            return self(category)

    def __get(self, item):
        lookup = self.__phrases.get(item)
        if lookup is None:
            lookup = getattr(self, item)
        if lookup is None:
            raise KeyError('No part registered for `{}`'.format(item))
        return _select(lookup)

    def __repl_match(self, match):
        return self(match.group(1).strip())


class Pipeline(object):
    def __init__(self, *steps, **environment):
        self.__steps = steps
        self.__environment = dict(environment)

    def __call__(self, input, *environment):
        value = input
        for step in self.__steps:
            step = _select(step)
            if not step:
                break
            value = yield from _pipe(step, value, self, *environment)
        return value

    def __contains__(self, step):
        return step in self.__environment

    def __getitem__(self, step):
        return self.__environment[step]
