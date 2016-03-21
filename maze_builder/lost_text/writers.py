import time
import math
import string
import random
from maze_builder.random2 import weighted_choice

TWITTER_LIMIT = 140
TWITTER_LINK_SIZE = 23
TWITTER_LIMIT_WITH_IMAGE = TWITTER_LIMIT - TWITTER_LINK_SIZE


EPOCH = 1458172800


def day():
    return int(1 + (time.time() - EPOCH) / (24*60*60))


EXCLAMATIONS = {
    ('What', '?.'): 1,
    ('Hmm', '.!?'): 1,
    ('Yikes', '!'): 1,
    ('Nope', '.!?'): 1,
    ('Bleh', '.'): 1,
    ('Super', '!.'): 1,
    ('Geez', '!.'): 1,
    ('What on earth', '.?!'): 1,
    ('Gah', '.!'): 1,
    ('Hooray', '.!'): 1,
    ('Whoops', '.!'): 1,
    ('Oops', '.!'): 1,
    ('Uh-oh', '.!'): 1,
    ('Welp', '.!'): 1,
    ('Yay', '.!'): 1,
    ('Gee', '.!'): 1,
    ('Crikey', '.!'): 1,
    ('Voilà', '.!'): 1,
    ('Argh', '.!'): 1,
    ('Ugh', '.!'): 1,
    ('Ouch', '.!'): 1,
    ('Boom', '!'): 1,
    ('Ew', '!.'): 1,
    ('Ow', '!.'): 1,
    ('Yuck', '!.'): 1,
    ('Dagnabit', '!.'): 1,
    ('Blimey', '!.'): 1,
    ('Egads', '!.'): 1,
    ('Crud', '!.'): 1,
    ('Why', '!.?'): 1,
    ('Nuts', '!.'): 1,
    ('Rats', '!.'): 1,
    ('Fiddlesticks', '!.'): 1,
    ('D\'oh', '!.'): 1,
    ('Dang', '!.'): 1,
    ('Darn', '!.'): 1,
    ('Shoot', '!.'): 1,
    ('Frick', '!.'): 1,
    ('Frack', '!.'): 1,
    ('Tada', '!.'): 1,
    ('Aha', '!.'): 1,
    ('Bother', '!.'): 1,
    ('Good grief', '!.'): 1,
    ('What in tarnation', '!.'): 1,
    ('Snap', '!.'): 1,
    ('Bah', '!.'): 1,
    ('Ack', '!.'): 1,
    ('Blast', '!.'): 1,
    ('Oy vey', '!.'): 1,
    ('Uff da', '!.'): 1,
    ('Hey', '!.'): 1,
    ('Shucks', '!.'): 1,
    ('Sheesh', '!.'): 1,
    ('Glorious', '!.'): 1,
}

INVERTED_PUNCTUATION = {
    '?': '¿',
    '!': '¡',
}

STRIKES = {
    '\u0336': 20, # Long horiz stroke
    '\u0338': 6, # Tall angled stroke
    '\u0337': 3, # Short angled stroke
    '\u0335': 1, # Short horiz stroke
}


CHAR_ENDERS = {
    '--': 1,
    '---': 3,
    '----': 2,
    '- OH NO': 1,
    '- UH OH': 1,
    '': 1,
}


WORD_ENDERS = {
    ' BYE': 1,
    '...': 1,
    '…': 1,
    '++': 1,
    '>>>': 1,
    '﷽': 0.2,
}


def strike_all(text):
    strike = weighted_choice(STRIKES)
    return ''.join(c + strike for c in str(text))

def strike(text):
    text = str(text)
    if random.random() < 0.2:
        return strike_all(text)
    else:
        return strike_all(text[:int((0.2 + 0.8*random.random())*(1+len(text)))])


NEGATIVE_STATUSES = {  # Used as '{}' or 'I'm so {}...'
    'hungry': 1,
    'cold': 1,
    'tired': 1,
    'exhausted': 1,
    'defeated': 1,
    'worn out': 1,
    'ravenous': 1,
    'faint': 1,
    'empty': 1,
    'hollow': 1,
    'insatiable': 1,
    'famished': 1,
    'unsatisfied': 1,
    'beat': 1,
    'annoyed': 1,
    'bored': 1,
    'distressed': 1,
    'drained': 1,
    'exasperated': 1,
    'fatigued': 1,
    'sleepy': 1,
    'collapsing': 1,
    'jaded': 1,
    'overtaxed': 1,
    'spent': 1,
    'wasted': 1,
    'worn': 1,
    'burned out': 1,
    'done for': 1,
    'lost': 20,
    'desolate': 1,
    'lonesome': 1,
    'alone': 1,
    'spiritless': 1,
    'sick and tired': 1,
    'sick': 1,
    'unenthusiastic': 1,
    'unenergetic': 1,
    'adrift': 1,
    'disoriented': 10,
    'astray': 1,
    'off-course': 10,
    'perplexed': 2,
    'bewildered': 2,
    'confused': 5,
    'contrite': 1,
    'unsettled': 1,
    'puzzled': 5,
    'ailing': 1,
    'ill': 1,
    'debilitated': 1,
    'frail': 1,
    'impaired': 1,
    'nauseated': 2,
    'bedridden': 1,
    'not so hot': 1,
    'under the weather': 1,
    'run down': 1,
    'unhealthy': 1,
    'unwell': 1,
    'weak': 1,
    'laid-up': 1,
    'rotten': 1,
    'anemic': 1,
    'feeble': 1,
    'confused': 10,
    'fragile': 1,
    'hesitant': 2,
    'powerless': 1,
    'uncertain': 5,
    'shaky': 1,
    'sickly': 1,
    'sluggish': 1,
    'slow': 1,
    'unsteady': 1,
    'weakened': 1,
    'wobbly': 1,
    'puny': 1,
    'out of gas': 1,
    'irresolute': 1,
    'spent': 1,
    'infirm': 1,
    'chilled': 1,
    'frozen': 1,
    'frigid': 1,
    'raw': 1,
    'numbed': 1,
    'benumbed': 1,
    'thirsty': 1,
    'parched': 1,
    'injured': 10,
    'afraid': 1,
    'terrified': 1,
    'anxious': 1,
    'apprehensive': 1,
    'frightened': 1,
    'nervous': 1,
    'scared': 1,
    'cowardly': 1,
    'daunted': 1,
    'discouraged': 1,
    'disheartened': 1,
    'dismayed': 1,
    'distressed': 1,
    'horrified': 1,
    'panic-stricken': 1,
    'petrified': 1,
    'scared stiff': 1,
    'scared to death': 1,
    'terror-stricken': 1,
    'humbled': 1,
    'dead': 1,
    'naked': 1,
    'wild': 1,
    'uncivilized': 1,
    'scorched': 1,
    'withered': 1,
    'sunburned': 1,
    'windburned': 1,
    'frostbitten': 1,
    'dehydrated': 1,
    'shriveled': 1,
    'dried up': 1,
    'dried out': 1,
    'smelly': 1,
    'stinky': 1,
    'noxious': 1,
    'putrid': 1,
    'revolting': 1,
    'grody': 1,
    'gross': 1,
    'icky': 1,
}

GREAT_PAINS = {
    'diarrhea': 10,
    'pain': 10,
    'hurts': 10,
    'giardia': 1,
}

INTENSIFIERS = {
    'awfully {}': 1,
    'amazingly {}': 1,
    'cursedly {}': 1,
    'critically {}': 1,
    'deathly {}': 1,
    'meagerly {}': 0.2,
    'super-{}': 1,
    'devastatingly {}': 1,
    'terribly {}': 1,
    'dreadfully {}': 1,
    'wickedly {}': 1,
    'disgracefully {}': 1,
    'completely {}': 1,
    'reprehensibly {}': 1,
    'unforgivably {}': 1,
    'unpleasantly {}': 1,
    'wretchedly {}': 1,
}

NEGATIVE_SENTENCES = {
    '{}.': 30,
    '{}!': 10,
    '{} again?': 10,
    '{} now.': 2,
    '{} here.': 5,
    '{} here!': 2,
    '{}. Now I know what that means.': 1,
    '{}: and not for the first time.': 1,
    '{} -- and not for the first time.': 1,
    '{}? Yes, always.': 1,
    'I feel {}.': 10,
    'I feel so {}.': 5,
    'I feel so {}!': 5,
    'I\'m {}.': 10,
    'I\'m so {}.': 5,
    'Will I always be so {}?': 1,
    'Why am I so {}?': 1,
    'No one knows how {} I am.': 1,
    'Has anyone ever been so {} before?': 1,
    'Has anyone ever been so {}?': 1,
    'Has anyone ever felt so {}?': 1,
    'I never want to feel this {} again.': 1,
    'I hope I\'ll never be so {} again.': 1,
    'I can\'t stand being so {}.': 1,
    'I\'ve never been so {}.': 1,
    'I\'ve never been so {} before.': 1,
    'Before this trip, I\'d never been so {}.': 1,
    'At home, no one is ever so {}.': 1,
    'So {} a person can be.': 1,
    'So {} a person can feel.': 1,
    'I never knew what it was like to be so {}.': 1,
    'No one has ever been so {}.': 1,
    'I could write a book about being so {}.': 1,
    'Even in my dreams, I\'m {}.': 1,
    'I\'m as {} as I\'ve ever been.': 1,
    'Why does God allow us to be so {}?': 1,
    'Would I have come this way, if I\'d known I\'d be so {}?': 1,
}

LOST_SENTENCES = {
    "Am I going in circles?": 1,
    "It's impossible to guess which way to go.": 1,
    "I'm just guessing at this point.": 1,
    "One way's as good as another.": 1,
    "A map would be nice.": 1,
    "It's unmappable.": 1,
    "Are the walls... moving?": 1,
    "How am I supposed to solve this?": 1,
    "If only someone could point the way.": 1,
    "I hope I don't die here.": 1,
    "This was a mistake.": 1,
    "Here again?": 1,
    "I remember a time before all this...": 1,
    "There's just no way!": 1,
    "Every place is like every other.": 1,
    "I'm in a maze of twisty little passages, all alike.": 0.2,
    "Am I even making progress?": 1,
    "Will I get out alive?": 1,
    "Is it still possible to escape?": 1,
    "Which way did I even come from?": 1,
    "Where did I come from?": 1,
    "Where am I going?": 1,
    "Where should I go?": 1,
    "Taking some time to find my bearings.": 1,
    "This is impossible.": 1,
    "This is taking so long.": 1,
    "This is so hard.": 1,
    "I've tried so hard.": 1,
    "I can't believe this.": 1,
    "I can't understand it.": 1,
    "I don't get it.": 1,
    "Is this progress?": 1,
    "Off the map.": 1,
    "That's not on my map!": 1,
    "Ask for directions? I wish I could.": 1,
    "I feel I've been here all my life.": 1,
    "I wonder if anyone remembers me.": 1,
    "I called down each passage -- but got no response.": 1,
}

DIRECTIONS = {
    'north': 20,
    'south': 20,
    'east': 20,
    'west': 20,
    'up': 10,
    'down': 10,
    'around': 10,
    'forward': 5,
    'back': 5,
    'backward': 1,
    'over': 5,
    'under': 5,
    'through': 5,
    'out': 5,
    'in': 5,
    'left': 1,
    'right': 1,
    'clockwise': 5,
    'counter-clockwise': 5,
    'widdershins': 2,
    'out of here': 1,
}

DIRECTIONLESS_SENTENCES = { # North, south, up, down, etc.
    "{}.": 1,
    "{} again?": 1,
    "Which way is {}?": 1,
    "Is there a way {}?": 1,
    "Can I find a way {}?": 1,
    "Looking for a way {}.": 1,
    "No way {}!": 1,
    "There must be a way {}!": 1,
    "One route must go {}.": 1,
    "I'll go {}.": 1,
    "I'm going {}.": 1,
    "Someone suggested going {}.": 1,
    "I'd go {} if I could figure out what way that was.": 1,
    "I'll try going {} for awhile.": 1,
    "Heading {}.": 1,
    "Bearing {}.": 1,
    "Going {}.": 1,
    "I can't figure out which way goes {}.": 1,
    "I'll spend some time finding the way {}.": 1,
    "If only the way {} were marked somehow!": 1,
    "If only I could find the way {}!": 1,
    "I thought I knew the way {}!": 1,
    "I wish I'd mapped the way {}!": 1,
    "I once learned how to find the way {} -- but I've forgotten.": 1,
    "I thought I knew the way {} -- did I forget?": 1,
}

ROOM_SENTENCES = {
    "A {}.": 15,
    "{}.": 5,
    "Another {}.": 8,
    "I'll stay in this {} a while.": 1,
    "Should I spend the night in this {}?": 1,
    "I awoke in this {}.": 1,
    "Yet another {}.": 3,
    "I tire of coming across another {}.": 0.5,
    "Not another {}!": 1,
    "I find myself in a {}.": 1,
    "Setting up camp in this {}.": 1,
    "Taking a break in this {}.": 1,
    "Sitting in a {}.": 1,
    "Searched a {}.": 1,
    "Found a {}.": 1,
    "Claiming this {}.": 1,
    "I remember this {}.": 1,
    "This {} again?": 1,
    "Fell into a {}.": 1,
    "Lunched in a {}.": 1,
    "Snacking in a {}.": 1,
}

ROOM_DESCRIPTORS = {
    '{}': 15,
    'musty {}': 1,
    'dusty {}': 1,
    'horrid {}': 1,
    'awful {}': 1,
    'unpleasant {}': 1,
    'unlit {}': 1,
    'dark {}': 1,
    'drafty {}': 1,
    'comfortless {}': 1,
    'little {}': 1,
    'dusty {}': 1,
    'forsaken {}': 1,
    'lonely {}': 1,
    'uninhabited {}': 1,
    'unwelcoming {}': 1,
    'chilly {}': 1,
    'godforsaken {}': 1,
    'featureless {}': 1,
    'abandoned {}': 1,
    'deserted {}': 1,
    '{} like any other': 1,
}

GENERIC_ROOM_TYPES = {
    'room': 10,
    'place': 10,
    'space': 10,
    'cell': 10,
    'alcove': 10,
    'chamber': 10,
    'corridor': 10,
    'hallway': 10,
    'hall': 10,
    'passage': 10,
    'area': 10,
    'lobby': 2,
    'entry': 2,
    'hole': 1,
    'maze': 1,
    'entranceway': 5,
}

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


def _fix_sentence(sentence):
    if not sentence[0].isupper():
        sentence = sentence[0].upper() + sentence[1:]
    for key, value in SENTENCE_FIXES.items():
        if key in sentence:
            sentence = sentence.replace(key, value)
    return sentence


class LostTextWriter(object):
    def __init__(self, limit=TWITTER_LIMIT_WITH_IMAGE):
        self.limit = limit

        self.states = {
            'intro': {
                'negative_status': 7,
                'pre_generic_room': 1,
                'generic_room': 4,
                'lost_sentence': 1,
                'directionless_sentence': 1,
            },
            'negative_status': {
                'lost_sentence': 5,
                'directionless_sentence': 5,
                'pre_generic_room': 0.6,
                'generic_room': 1.4,
                'finished': 2,
            },
            'pre_generic_room': {
                'generic_room': 5,
                'lost_sentence': 1,
                'directionless_sentence': 1,
            },
            'generic_room': {
                'negative_status': 1,
                'lost_sentence': 2,
                'directionless_sentence': 2,
                'finished': 1,
            },
            'lost_sentence': {
                'directionless_sentence': 1,
                'finished': 1,
            },
            'directionless_sentence': {
                'lost_sentence': 1,
                'finished': 1,
            }
        }

    def write(self):
        last_text, text = '', ''
        state = 'intro'
        for _ in range(100):
            last_text, text = text, getattr(self, state)(text)
            if len(text) > self.limit:
                break
            state = weighted_choice(self.states.get(state, [None]))
            if not state or not hasattr(self, state):
                break

        text = text.rstrip()
        if len(text) <= self.limit:
            return text
        elif random.random() < 0.50:
            if random.random() < 0.50:
                ender = weighted_choice(CHAR_ENDERS)
                return text[:self.limit - len(ender)] + ender
            else:
                ender = weighted_choice(WORD_ENDERS)
                while len(text) + len(ender) > self.limit:
                    text, _ = text.rsplit(None, 1)
                return text + ender
        else:
            return last_text.rstrip()[:self.limit]

    def intro(self, text):
        return weighted_choice({
            self.intro_day: 5,
            self.intro_day_slightly_confused: 2,
            self.intro_day_moderately_confused: 1,
            self.intro_day_very_confused: 1,
        })(text)

    def intro_day(self, text):
        day_formats = {
            'Day {}.': 50,
            'Day {}!': 4,
            'It is day {}.': 4,
            'Day {} at last!': 1,
            'Day {} of this trip.': 1,
            'Day {} is here.': 1,
            'Day {} arrives.': 1,
            'Day {}, of course.': 1,
            'Day {} still?': 1,
        }
        number = day()
        return text + weighted_choice(day_formats).format(number) + ' '

    def intro_day_slightly_confused(self, text):
        day_formats = {
            'Day {}?'.format: 20,
            'Is it day {}?'.format: 5,
            'Day {}, I think.'.format: 2,
            'Day {}, if I\'m correct.'.format: 1,
            'Day {}, I believe.'.format: 1,
            'Pretty sure this is day {}.'.format: 1,
            'Day {} still?'.format: 1,
            'Day {}, I hope.'.format: 1,
            (lambda x: strike_all('Day {}.'.format(x))): 1,
        }
        number = day() + random.choice([-2, -1, -1, 0, 0, 0, 1, 1, +2])
        return text + weighted_choice(day_formats)(number) + ' '

    def intro_day_moderately_confused(self, text):
        day_formats = {
            'Day {} -- or is it {}?'.format: 1,
            'Day {} -- or {}?'.format: 5,
            'Day {} or {}.'.format: 1,
            'Day {1}, or possibly {0}.'.format: 1,
            'Day {}, or {} -- something like that.'.format: 1,
            (lambda x, y: 'Day {} {}.'.format(strike_all(x), y)): 1,
        }
        number = day() + random.randint(-2, +1)
        return text + weighted_choice(day_formats)(number, number+1) + ' '

    def intro_day_very_confused(self, text):
        day_formats = {
            'Day ???': 3,
            'Day ????': 2,
            'Day ?????': 1,
            'Day ??????': 1,
            'Day #??': 1,
            'Day #???': 1,
            'Day #????': 1,
            'Day #?????': 1,
            'Day unknown.': 1,
            'Day. Night. Whatever.': 1,
            'Who cares what day it is.': 1,
            'No idea what day this is.': 1,
            'Who counts the days here?': 1,
            'Another day.': 1,
            'The days fade into each other.': 1,
            'The days -- they\'re all the same.': 1,
            strike_all('Day'): 1,
        }
        return text + weighted_choice(day_formats) + ' '

    def pre_generic_room(self, text):
        return self._exclaim(text)

    def generic_room(self, text):
        room = weighted_choice(ROOM_DESCRIPTORS).format(weighted_choice(GENERIC_ROOM_TYPES))
        sentence = weighted_choice(ROOM_SENTENCES).format(room)

        return text + _fix_sentence(sentence) + ' '

    def negative_status(self, text):
        parts = list()

        status = weighted_choice(NEGATIVE_STATUSES)
        if random.random() < 0.5:
            status = weighted_choice(INTENSIFIERS).format(status)
        status = weighted_choice(NEGATIVE_SENTENCES).format(status)

        return text + _fix_sentence(status) + ' '

    def lost_sentence(self, text):
        sentence = weighted_choice(LOST_SENTENCES)
        if random.random() < 0.1:
            sentence = strike(sentence)
        return text + sentence + ' '

    def directionless_sentence(self, text):
        sentence = _fix_sentence(weighted_choice(DIRECTIONLESS_SENTENCES).format(weighted_choice(DIRECTIONS)))
        if random.random() < 0.2:
            sentence = strike(sentence)
        return text + sentence + ' '

    def _exclaim(self, text):
        exclamation, punctuation = weighted_choice(EXCLAMATIONS)
        punctuation = random.choice(punctuation)
        if random.random() < 0.25:
            if punctuation == '?':
                if random.random() < 0.5:
                    punctuation = '?' * random.randint(2, 6)
                elif random.random() < 0.7:
                    punctuation = ''.join(random.choice('!?') for _ in range(random.randint(1, 6))) + '?'
                elif random.random() < 0.7:
                    punctuation = ''.join(random.choice('!?‽?') for _ in range(random.randint(1, 6))) + '?'
                else:
                    punctuation = '‽'
            elif punctuation == '!':
                punctuation = '!' * random.randint(2, 6)
            elif punctuation == '.':
                punctuation = random.choice(('...', '…', '...!', '…!'))

        if not punctuation.endswith('?') and random.random() < 0.02:
            punctuation += '(?)'
        elif not punctuation.endswith('!') and random.random() < 0.02:
            punctuation += '(!)'

        if random.random() < 0.02 and punctuation in INVERTED_PUNCTUATION:
            exclamation = INVERTED_PUNCTUATION[punctuation] + exclamation

        return '{}{}{} '.format(text, exclamation, punctuation)

    def finished(self, text):
        return text


if __name__ == '__main__':
    for i in range(24):
        print(LostTextWriter().write())

