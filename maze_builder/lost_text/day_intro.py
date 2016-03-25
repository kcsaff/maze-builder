import time
from maze_builder.random2 import weighted_choice
from maze_builder.sewer import MadLibs, Choice
from maze_builder.lost_text.text_decorations import strike_all


EPOCH = 1458172800  # Roughly when the bot started


def day(offset=0):
    return int(offset) + int(1 + (time.time() - EPOCH) / (24*60*60))

prechosen_wrong_day = day(weighted_choice({-1: 1, 0: 1, 1: 1}))


intro_sentence = MadLibs({
        '{TODAY EXACT}': 1,
        '{SLIGHT}': 1,
        '{VERY}': 1,
    },
    STRUCK=strike_all,
    YESTERDAY=day(-1),
    TODAY=day(),
    TOMORROW=day(+1),
    WRONG_YESTERDAY=prechosen_wrong_day-1,
    WRONG_TODAY=prechosen_wrong_day,
    WRONG_TOMORROW=prechosen_wrong_day+1,
    SLIGHTLY_UNCERTAIN_DAY={
        '{YESTERDAY}': 1,
        '{TODAY}':     5,
        '{TOMORROW}':  2,
    },
    EXACT={
        'Day {}.': 50,
        'Day {}!': 4,
        'It is day {}.': 4,
        'Day {} at last!': 1,
        'Day {} of this trip.': 1,
        'Day {} is here.': 1,
        'Day {} arrives.': 1,
        'Day {}, of course.': 1,
        'Day {} still?': 1,
    },
    SLIGHT={
        'Day {SLIGHTLY_UNCERTAIN_DAY}?': 20,
        'Is it day {TOMORROW}?': 5,
        'Day {SLIGHTLY_UNCERTAIN_DAY}, I think.': 2,
        'Day {SLIGHTLY_UNCERTAIN_DAY}, if I\'m correct.': 1,
        'Day {SLIGHTLY_UNCERTAIN_DAY}, I believe.': 1,
        'Pretty sure this is day {SLIGHTLY_UNCERTAIN_DAY}.': 1,
        'Day {SLIGHTLY_UNCERTAIN_DAY} still?': 1,
        'Day {SLIGHTLY_UNCERTAIN_DAY}, I hope.': 1,
        '{SLIGHTLY_UNCERTAIN_DAY EXACT STRUCK}': 1,
    },
    MODERATE={
        'Day {WRONG_TODAY} -- or is it {WRONG_TOMORROW}?': 1,
        'Day {WRONG_TODAY} -- or {WRONG_TOMORROW}?': 5,
        'Day {WRONG_TODAY} or {WRONG_TOMORROW}.': 1,
        'Day {WRONG_TOMORROW}, or possibly {WRONG_TODAY}.': 1,
        'Day {WRONG_TODAY}, or {WRONG_TOMORROW} -- something like that.': 1,
        'Day {WRONG_TODAY STRUCK} {WRONG_TOMORROW}.': 1,
    },
    VERY={
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
)
