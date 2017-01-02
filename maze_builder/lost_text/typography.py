import re


QUOTE_PATTERN = re.compile(r'(?:\s|^|\p)(\'\S.*\S\'|"\S.*\S"|“.*”|‘.*’)(?:\s|$|\p)')
QUOTE_PATTERN_GROUP = 1

PRIME_PATTERNS = [
    re.compile(r'(?<=\d)(\'|′)(?=[^a-zA-Z])'),
    re.compile(r'(?<=\d)(\'\'|"|′′|″)(?=[^a-zA-Z])'),
    re.compile(r'(?<=\d)(\'\'\'|′′′|‴|"\')(?=[^a-zA-Z])'),
    re.compile(r'(?<=\d)(\'\'\'\'|""|′′′′|″″|⁗)(?=[^a-zA-Z])'),
]

ELLIPSIS_PATTERN = re.compile(r'\.\.\.|…')

APOSTROPHE_PATTERN = re.compile(r'(?<=\w)(\'|′)(?=\s|[a-z]|$)')

EMDASH_PATTERN = re.compile(r'[ ]?(--+|—)[ ]?|[ ](–|-)[ ]')

ENDASH_PATTERN = re.compile(r'–|(?<=\d)-(?=\d)')

def quote(phrase, quotes=('“', '”'), innerquotes=('‘', '’')):
    """

    >>> quote("It's okay.", '""', "''")
    '"It\\'s okay."'

    >>> quote("It's okay", '""', "''")
    '"It\\'s okay"'

    >>> quote("'It's okay.'", '""', "''")
    '"\\'It\\'s okay.\\'"'

    >>> quote("It's 'okay.'", '""', "''")
    '"It\\'s \\'okay.\\'"'

    >>> quote('I said, "It\\'s okay."', '""', "''")
    '"I said, \\'It\\'s okay.\\'"'

    >>> quote("It’s okay.")
    '“It’s okay.”'

    >>> quote("It’s okay")
    '“It’s okay”'

    >>> quote("'It’s okay.'")
    '“‘It’s okay.’”'

    >>> quote("It’s 'okay.'")
    '“It’s ‘okay.’”'

    >>> quote('I said, "It’s okay."')
    '“I said, ‘It’s okay.’”'

    >>> quote('I said, “It’s okay.”')
    '“I said, ‘It’s okay.’”'
    """
    return ''.join(_quote_parts(phrase, quotes, innerquotes))


def _quote_parts(phrase, quotes=('“', '”'), innerquotes=('‘', '’')):
    yield quotes[0]
    start = 0
    for match in QUOTE_PATTERN.finditer(phrase):
        yield phrase[start:match.start(QUOTE_PATTERN_GROUP)]
        yield from _quote_parts(match.group(QUOTE_PATTERN_GROUP)[1:-1], innerquotes, quotes)
        start = match.end(QUOTE_PATTERN_GROUP)
    yield phrase[start:]
    yield quotes[-1]


FINAL_UNICODE = {
    "'": '’',
    '"': '″',
    '...': '…',
}


FINAL_ASCII = {
    '‘': "'",
    '’': "'",
    '“': '"',
    '”': '"',
    '…': '...',
    '′': "'",
    '″': '"',
    '‴': '"\'',
    '⁗': '""',
    '—': '--',
    '–': '-',
}


UNICODE_AMERICAN_TYPOGRAPHY = dict(
        quotes=('“', '”'),
        innerquotes=('‘', '’'),
        apostrophe='’',
        primes=('′', '″', '‴', '⁗'),
        ellipsis='…',
        emdash='—',
        endash='–',
        final=FINAL_UNICODE.items(),
)


UNICODE_BRITISH_TYPOGRAPHY = dict(
        quotes=('‘', '’'),
        innerquotes=('“', '”'),
        apostrophe='’',
        primes=('′', '″', '‴', '⁗'),
        ellipsis='…',
        emdash=' – ',
        endash='–',
        final=FINAL_UNICODE.items(),
)


ASCII_AMERICAN_TYPOGRAPHY = dict(
        quotes=('"', '"'),
        innerquotes=('\'', '\''),
        apostrophe='\'',
        primes=('\'', '"', '"\'', '""'),
        ellipsis='...',
        emdash=' -- ',
        endash='-',
        final=FINAL_ASCII.items(),
)


ASCII_BRITISH_TYPOGRAPHY = dict(
        quotes=('\'', '\''),
        innerquotes=('"', '"'),
        apostrophe='\'',
        primes=('\'', '"', '"\'', '""'),
        ellipsis='...',
        emdash=' - ',
        endash='-',
        final=FINAL_ASCII.items(),
)


def fix_typography(
        sentence,
        quotes=('“', '”'),
        innerquotes=('‘', '’'),
        apostrophe='’',
        primes=('′', '″', '‴', '⁗'),
        ellipsis='…',
        emdash='—',
        endash='–',
        final=FINAL_UNICODE.items(),
):
    sentence = quote(sentence, innerquotes, quotes)[1:-1]
    for prime, pattern in reversed(list(zip(primes, PRIME_PATTERNS))):
        sentence = pattern.sub(prime, sentence)
    if apostrophe:
        sentence = APOSTROPHE_PATTERN.sub(apostrophe, sentence)
    if ellipsis:
        sentence = ELLIPSIS_PATTERN.sub(ellipsis, sentence)
    if emdash:
        sentence = EMDASH_PATTERN.sub(emdash, sentence)
    if endash:
        sentence = ENDASH_PATTERN.sub(endash, sentence)
    if final:
        for key, value in final:
            if key in sentence:
                sentence = sentence.replace(key, value)
    return sentence
