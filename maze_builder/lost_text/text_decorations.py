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


PHRASE_FIXES = {
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


def pluralize_verb(verb):
    return ' '.join(word[:-1] if word.endswith('s') else word for word in verb.split())


def strike_all(text):
    strike = STRIKES()
    return ''.join(c + strike for c in str(text))


def strike(text):
    text = str(text)
    if random.random() < 0.2:
        return strike_all(text)
    else:
        return strike_all(text[:int((0.2 + 0.8*random.random())*(1+len(text)))])


def _first_character_index(sentence, ignored=set('\'" \t\n')):
    for i, c in enumerate(sentence):
        if c not in ignored:
            return i
    else:
        return 0


def fix_sentence(sentence):
    first = _first_character_index(sentence)
    if not sentence[first].isupper():
        sentence = sentence[:first] + sentence[first].upper() + sentence[first + 1:]
    return fix_phrase(sentence)


def fix_phrase(phrase):
    phrase = ' ' + phrase

    for key, value in PHRASE_FIXES.items():
        if key in phrase:
            phrase = phrase.replace(key, value)

    return phrase[1:]


ROMAN_NUMERALS_UNICODE_UPPER=[
    ('ↂ', 10000),
    ('ↁ', 5000),
    ('Ⅿ', 1000),
    ('ⅭⅯ', 900),
    ('Ⅾ', 500),
    ('ⅭⅮ', 400),
    ('Ⅽ', 100),
    ('ⅩⅭ', 90),
    ('Ⅼ', 50),
    ('ⅩⅬ', 40),
    ('Ⅻ', 12, True),
    ('Ⅺ', 11, True),
    ('Ⅹ', 10),
    ('Ⅸ', 9),
    ('Ⅷ', 8),
    ('Ⅶ', 7),
    ('Ⅵ', 6),
    ('Ⅴ', 5),
    ('Ⅳ', 4),
    ('Ⅲ', 3),
    ('Ⅱ', 2),
    ('Ⅰ', 1),
]


ROMAN_NUMERALS_ASCII_UPPER=[
    ('M', 1000),
    ('CM', 900),
    ('D', 500),
    ('CD', 400),
    ('C', 100),
    ('XC', 90),
    ('L', 50),
    ('XL', 40),
    ('X', 10),
    ('V', 5),
    ('IV', 4),
    ('I', 1),
]


def roman_numerals(number, numerals=ROMAN_NUMERALS_UNICODE_UPPER):
    """

    >>> roman_numerals(456, ROMAN_NUMERALS_ASCII_UPPER)
    'CDLVI'
    """
    parts = list()
    number = int(number)
    for item in numerals:
        if len(item) == 2:
            numeral, value = item
            exact = False
        else:
            numeral, value, exact = item
        if exact:
            if value == number:
                parts.append(numeral)
                break
            else:
                continue
        while number >= value:
            parts.append(numeral)
            number -= value
    return ''.join(parts)


COUNTING_RODS=[
    '〇' +''.join(chr(i) for i in range(0x1D360, 0x1D369)),
    '〇' +''.join(chr(i) for i in range(0x1D369, 0x1D372)),
]


def counting_rods(number, numerals=COUNTING_RODS):
    parts = list()
    power = 0
    if number == 0:
        return numerals[0][0]
    while number > 0:
        numeral_set = numerals[power % len(numerals)]
        base = len(numeral_set)
        parts.append(numeral_set[number % base])
        number //= base
        power += 1
    return ''.join(reversed(parts))


if __name__ == '__main__':
    print(fix_sentence('Maybe I can build a amazing GPS from 3 threads.'))

    import doctest
    doctest.testmod()