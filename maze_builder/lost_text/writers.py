import time
import math
import string
import random
from maze_builder.random2 import weighted_choice
from maze_builder.sewer import Choice, Pipeline, Selector

from maze_builder.lost_text.directionless import directionless_sentence
from maze_builder.lost_text.lost import lost_sentence
from maze_builder.lost_text.negative_status import negative_status_sentence
from maze_builder.lost_text.nasty_rooms import nasty_room_sentence
from maze_builder.lost_text.text_decorations import strike_all
from maze_builder.lost_text.exclamations import exclaim_appending
from maze_builder.lost_text.day_intro import intro_sentence
from maze_builder.lost_text.macgyver import macgyver_sentence
from maze_builder.lost_text.clues import clue_sentence
from maze_builder.lost_text.quotes import quote_sentence
from maze_builder.lost_text.nearby import generate_routes
from maze_builder.lost_text.missing import missing_sentence

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


class LostTextWriter(object):
    def __init__(self, limit=TWITTER_LIMIT_WITH_IMAGE):
        self.limit = limit

        self.states = Pipeline(
            'intro',
            intro=Pipeline(
                intro_sentence.appending,
                Choice(
                    negative_status=4,
                    pre_generic_room=2,
                    generic_room=5,
                    lost_sentence=2,
                    directionless_sentence=2,
                    macgyver=2,
                    clue=5,
                    quote_sentence=3,
                    nearby=3,
                    missing=5,
                ),
            ),
            missing=Pipeline(
                missing_sentence.appending,
                Choice(
                    lost_sentence=1,
                    directionless_sentence=1,
                    finished=3,
                )
            ),
            clue=Pipeline(
                clue_sentence.appending,
                Choice(
                    finished=4,
                    macgyver=2,
                    pre_generic_room=1,
                    nearby=1,
                )
            ),
            negative_status=Pipeline(
                negative_status_sentence.appending,
                Choice(
                    lost_sentence=3,
                    directionless_sentence=4,
                    generic_room=1,
                    finished=2,
                    macgyver=3,
                    nearby=1,
                    missing=3,
                )
            ),
            pre_generic_room=Pipeline(
                exclaim_appending,
                Choice(
                    generic_room=5,
                    lost_sentence=1,
                    directionless_sentence=1,
                    nearby=2,
                )
            ),
            generic_room=Pipeline(
                nasty_room_sentence.appending,
                Choice(
                    negative_status=1,
                    lost_sentence=2,
                    directionless_sentence=2,
                    finished=1,
                    macgyver=3,
                    clue=4,
                    quote_sentence=1,
                    nearby=2,
                    missing=2,
                )
            ),
            lost_sentence=Pipeline(
                lost_sentence.appending,
                Choice(
                    directionless_sentence=2,
                    finished=2,
                    macgyver=1,
                    nearby=1,
                )
            ),
            directionless_sentence=Pipeline(
                directionless_sentence.appending,
                Choice(
                    lost_sentence=2,
                    finished=2,
                    macgyver=1,
                    nearby=1,
                )
            ),
            quote_sentence=Pipeline(
                quote_sentence.appending,
                Choice(
                    finished=2,
                    nearby=1,
                )
            ),
            macgyver=Pipeline(
                macgyver_sentence.appending,
                Choice(
                    lost_sentence=4,
                    finished=4,
                    quote_sentence=1,
                    nearby=1,
                )
            ),
            nearby=Pipeline(
                lambda text: generate_routes(text, limit),
                Choice(
                    lost_sentence=4,
                    finished=4,
                    directionless_sentence=2,
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
        elif random.random() < 0.15:
            if random.random() < 0.25:
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

