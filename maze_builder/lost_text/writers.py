import time
import math
import string
import random
from maze_builder.random2 import weighted_choice
from maze_builder.sewer import Choice, Pipeline

from maze_builder.lost_text.directionless import directionless_sentence
from maze_builder.lost_text.lost import lost_sentence
from maze_builder.lost_text.negative_status import negative_status_sentence
from maze_builder.lost_text.nasty_rooms import nasty_room_sentence
from maze_builder.lost_text.text_decorations import strike_all
from maze_builder.lost_text.exclamations import exclaim
from maze_builder.lost_text.day_intro import intro_sentence

TWITTER_LIMIT = 140
TWITTER_LINK_SIZE = 23
TWITTER_LIMIT_WITH_IMAGE = TWITTER_LIMIT - TWITTER_LINK_SIZE


CHAR_ENDERS = {
    '--': 1,
    '---': 3,
    '----': 2,
    '- OH NO': 1,
    '- UH OH': 1,
    '': 1,
}


WORD_ENDERS = {
    '...': 1,
    '…': 1,
    '++': 1,
    '>>>': 1,
}

NAVIGATION_AIDS = {
    'sextant': 10,
    'compass': 10,
    'map': 10,
    'GPS': 10,
    'binoculars': 10,
    'navigation chart': 10,
    'sonar': 1,
}


WORTHLESS_FINDS = { #  Should be pluralizable with 's'
    'stick': 1,
    'stone': 1,
    'rock': 1,
    'feather': 1,
    'pebble': 1,
    'tin can': 1,
    'pencil nub': 1,
    'thread': 1,
    'string': 1,
}


WORTHLESS_MODIFIERS = {
    'fancy {}': 1,
    'ugly {}': 1,
    'crumbling {}': 1,
}


class LostTextWriter(object):
    def __init__(self, limit=TWITTER_LIMIT_WITH_IMAGE):
        self.limit = limit

        self.states = Pipeline(
            Choice(
                negative_status=7,
                pre_generic_room=1,
                generic_room=4,
                lost_sentence=1,
                directionless_sentence=1,
            ),
            negative_status=Pipeline(
                negative_status_sentence.appending,
                Choice(
                    lost_sentence=5,
                    directionless_sentence=5,
                    pre_generic_room=0.6,
                    generic_room=1.4,
                    finished=2,
                )
            ),
            pre_generic_room=Pipeline(
                negative_status_sentence.appending,
                Choice(
                    generic_room=5,
                    lost_sentence=1,
                    directionless_sentence=1,
                )
            ),
            generic_room=Pipeline(
                negative_status_sentence.appending,
                Choice(
                    negative_status=1,
                    lost_sentence=2,
                    directionless_sentence=2,
                    finished=1,
                )
            ),
            lost_sentence=Pipeline(
                lost_sentence.appending,
                Choice(
                    directionless_sentence=1,
                    finished=1,
                )
            ),
            directionless_sentence=Pipeline(
                directionless_sentence.appending,
                Choice(
                    lost_sentence=1,
                    finished=1,
                )
            ),
            finished=None,
        )

    def write(self):
        last_text = ''
        for text in self.states.pipe(''):
            if len(text) > self.limit:
                break
            last_text = text

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


if __name__ == '__main__':
    for i in range(24):
        print(LostTextWriter().write())

