import random
from maze_builder.sewer import Choice


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
