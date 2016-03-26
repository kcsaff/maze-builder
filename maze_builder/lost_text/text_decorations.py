import random
import re
from maze_builder.sewer import Choice

UNCHANGING_PLURALS = {
    'bison', 'buffalo', 'deer', 'fish', 'moose', 'pike', 'plankton', 'salmon', 'sheep', 'squid', 'swine', 'trout',
}
UNCHANGING_PLURALS_BY_SIZE = {
    i: {plural for plural in UNCHANGING_PLURALS if len(plural)==i}
    for i in range(1, 1+max(len(plural) for plural in UNCHANGING_PLURALS))
}

IRREGULAR_PLURALS = {
    'man': 'men',
    'child': 'children',
    'foot': 'feet',
    'goose': 'geese',
    'tooth': 'teeth',
    'mouse': 'mice',
    'person': 'people',
    'leaf': 'leaves',
}
IRREGULAR_PLURALS_BY_SIZE = {
    i: {sing: plural for sing, plural in IRREGULAR_PLURALS.items() if len(sing)==i}
    for i in range(1, 1+max(len(sing) for sing in IRREGULAR_PLURALS))
}
LONE_IRREGULAR_PLURALS = {
    'ox': 'oxen',     # box -> boxes
    'louse': 'lice',  # blouse -> blouses
}

PLURALIZERS = [
    (re.compile(pattern), replacement)
    for (pattern, replacement) in [
        (r'(ies)$', r'\1'),
        (r'(\w+)((\s+|-)(of|from|about)(\s+|-)\w+)$', lambda match: pluralize(match.group(1)) + match.group(2)),
        (r'(s|x|sh|ch)$', r'\1es'),
        (r'([b-df-hj-np-tv-z])y$', r'\1ies'),
        (r'quy$', r'quies'),
        ('$', 's'),
]]


SENTENCE_FIXES = {
    ' a a': ' an a',
    ' a e': ' an e',
    ' a i': ' an i',
    ' a o': ' an o',
    ' a u': ' an u',
    'A a': 'An a',
    'A e': 'An e',
    'A i': 'An i',
    'A o': 'An o',
    'A u': 'An u',
}


STRIKES = Choice({
    '\u0336': 20,  # Long horiz stroke
    '\u0338': 6,   # Tall angled stroke
    '\u0337': 3,   # Short angled stroke
    '\u0335': 1,   # Short horiz stroke
})


def pluralize(item):
    """

    >>> pluralize('species')
    'species'
    >>> pluralize('bus')
    'buses'
    >>> pluralize('soliloquy')
    'soliloquies'
    >>> pluralize('box')
    'boxes'
    >>> pluralize('fish')
    'fish'
    >>> pluralize('starfish')
    'starfish'
    >>> pluralize('ash')
    'ashes'
    >>> pluralize('latch')
    'latches'
    >>> pluralize('baby')
    'babies'
    >>> pluralize('cow')
    'cows'
    >>> pluralize('piece of eight')
    'pieces of eight'
    >>> pluralize('box of destiny')
    'boxes of destiny'
    >>> pluralize('fish of destiny')
    'fish of destiny'
    >>> pluralize('starfish of destiny')
    'starfish of destiny'
    >>> pluralize('woman of destiny')
    'women of destiny'
    """
    if item in LONE_IRREGULAR_PLURALS:
        return LONE_IRREGULAR_PLURALS[item]
    if item in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[item]
    if item in UNCHANGING_PLURALS:
        return item
    if ' ' not in item:
        lower = item.lower()
        for size, words in IRREGULAR_PLURALS_BY_SIZE.items():
            if lower[-size:] in words:
                return item[:-size] + words[lower[-size:]]
        for size, words in UNCHANGING_PLURALS_BY_SIZE.items():
            if lower[-size:] in words:
                return item

    for pattern, replacement in PLURALIZERS:
        if pattern.search(item):
            return pattern.sub(replacement, item)
    return item


def strike_all(text):
    strike = STRIKES()
    return ''.join(c + strike for c in str(text))


def strike(text):
    text = str(text)
    if random.random() < 0.2:
        return strike_all(text)
    else:
        return strike_all(text[:int((0.2 + 0.8*random.random())*(1+len(text)))])


def fix_sentence(sentence):
    if not sentence[0].isupper():
        sentence = sentence[0].upper() + sentence[1:]
    for key, value in SENTENCE_FIXES.items():
        if key in sentence:
            sentence = sentence.replace(key, value)
    return sentence


if __name__ == '__main__':
    print(fix_sentence('Maybe I can build a amazing GPS from 3 threads.'))

    import doctest
    doctest.testmod()