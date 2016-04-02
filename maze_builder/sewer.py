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
from numbers import Number


def _select(obj, tag=None):
    if isinstance(obj, Selector):
        return _select(obj(tag=tag))
    else:
        return obj


def _pipe(fun, value, *environment, tag=None):
    fun = _select(fun, tag=tag)
    if fun is None:
        return value
    elif isinstance(fun, Pipeline):
        value = yield from fun.pipe(value, *environment, tag=tag)
    elif callable(fun):
        value = fun(value)
        received = yield value
        if received is not None:
            value = received
    else:
        for i, obj in enumerate(environment):
            if fun in obj:
                value = yield from _pipe(_select(obj[fun]), value, *environment[i:], tag=tag)
                break
        else:
            for env in environment:
                print(env)
            raise KeyError('No context contains key `{}`'.format(fun))
    return value


class Selector(object):
    def __init__(self, value=None, blessed=False):
        self.__value = value
        self.__blessed = blessed

    def __call__(self, tag=None):
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
    DEFAULT = 'default'

    def __init__(self, choices=(), **extras):
        self.random = random.uniform
        self.choices, self.weights = self.__build_choices_and_weights(choices, **extras)
        self.totals = collections.Counter()
        for weight in self.weights:
            self.totals.update(weight)

    def tags(self):
        tags = set()
        for weight in self.weights:
            tags.update(weight.keys())
        return tags

    def weighting(self, tag, weights):
        for weight in self.weights:
            weight.setdefault(tag, 0)
            weight[tag] += sum(w*weight.get(t, 0) for t, w in weights.items())
        return self

    def update(self, choices=(), **extras):
        choices, weights = self.__build_choices_and_weights(choices, **extras)
        self.choices += choices
        self.weights += weights
        for weight in self.weights:
            self.totals.update(weight)

    def __call__(self, tag=None):
        tag = tag or self.DEFAULT
        choices, weights, total = self.choices, self.weights, self.totals.get(tag, 0)

        # http://stackoverflow.com/a/17011134/1115497
        threshold = self.random(0, total)
        for choice, weight in zip(choices, weights):
            total -= weight.get(tag, 0)
            if total < threshold:
                return _select(choice)
        else:
            raise RuntimeError('Choice is empty')

    @classmethod
    def __build_choices_and_weights(cls, choices=(), **extras):
        if isinstance(choices, collections.Mapping):
            choices = choices.items()
        elif isinstance(choices, str):
            choices = ((choices, 1),)
        elif isinstance(choices, collections.Iterable):
            choices = collections.Counter(choices).items()

        choices, weights = zip(*itertools.chain(choices, extras.items()))

        weights = [
            {cls.DEFAULT: weight} if isinstance(weight, Number)
            else dict(weight) if isinstance(weight, dict)
            else {weight: 1} if isinstance(weight, str)
            else {tag: 1 for tag in weight} if isinstance(weight, collections.Sequence)
            else dict()
            for weight in weights
        ]

        return choices, weights


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

    def __call__(self, category=None, tag=None):
        if category is None:
            replacement = _select(self.__start)
            result = self.__RE_PATTERN.sub(self.__repl_match, str(replacement))
        else:
            if category is not None:
                category, *formats = category.split()
            replacement = self.__get(category, tag=tag)
            result = self.__RE_PATTERN.sub(self.__repl_match, str(replacement))
            for format in formats:
                result = self.format(result, format)
        return result

    def format(self, value, format=None):
        formatter = self.__get(format)
        formatter = formatter.format if not callable(formatter) else formatter
        return formatter(value)

    def appending(self, text='', category=None):
        if text:
            return text + ' ' + self(category)
        else:
            return self(category)

    def __get(self, item, tag=None):
        lookup = self.__phrases.get(item)
        if lookup is None:
            lookup = getattr(self, item)
        if lookup is None:
            raise KeyError('No part registered for `{}`'.format(item))
        return _select(lookup, tag=tag)

    def __repl_match(self, match):
        return self(match.group(1).strip())


class Pipeline(object):
    def __init__(self, *steps, **environment):
        self.__steps = steps
        self.__environment = dict(environment)

    def pipe(self, input, *environment, tag=None):
        value = input
        for step in self.__steps:
            step = _select(step, tag=tag)
            if not step:
                break
            value = yield from _pipe(step, value, self, *environment, tag=tag)
        return value

    def product(self, input, *environment, tag=None):
        result = input
        for result in self.pipe(input, *environment, tag=tag):
            pass
        return result

    def __contains__(self, step):
        return step in self.__environment

    def __getitem__(self, step):
        return self.__environment[step]
