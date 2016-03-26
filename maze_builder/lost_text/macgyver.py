from maze_builder.sewer import MadLibs, Choice
from maze_builder.lost_text.text_decorations import fix_sentence, pluralize

macgyver_sentence = MadLibs(
    '{MACGYVER FIXED}',
    FIXED=fix_sentence,
    PLURALIZED=pluralize,
    MACGYVER={
        'I could fix {MY_NAVIGATION_AID} if I had {A_DESIRED_WORTHLESS_TRINKET}.': 3,
        'Looking for {A_DESIRED_WORTHLESS_TRINKET}.': 1,
        'If only I had {A_NAVIGATION_AID}!': 2,
        'I need {A_NAVIGATION_AID}!': 2,
        '{A_NAVIGATION_AID} would be nice.': 2,
        '{MY_NAVIGATION_AID} broke!': 2,
        '{MY_NAVIGATION_AID} is broken.': 2,
        'I lost {MY_NAVIGATION_AID}.': 3,
        'I think I lost {MY_NAVIGATION_AID}.': 1,
        'Maybe I can build {A_NAVIGATION_AID} from {THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND}.': 2,
        'Trying to fashion {A_NAVIGATION_AID} out of {THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND}.': 2,
        'Planning to make {A_NAVIGATION_AID} out of {THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND}.': 2,
        'Making {A_NAVIGATION_AID} out of {THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND}.': 4,
        'I\'d trade {THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND} for {A_NAVIGATION_AID}.': 1,
        'Can I make something with {THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND}?': 2,
        'There\'s {THESE_WORTHLESS_TRINKETS} here.': 2,
        'I found {THESE_WORTHLESS_TRINKETS}!': 1,
        'Dropping {THESE_WORTHLESS_TRINKETS}.': 2,
        'Why am I still carrying {THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND}?': 1,
    },
    A_NAVIGATION_AID={
        'a {NAVIGATION_AID MADE_WONDERFUL}': 20,
        'some {NAVIGATION_AIDS MADE_WONDERFUL}': 5,
    },
    MY_NAVIGATION_AID={
        'my {NAVIGATION_AID MADE_WONDERFUL}': 30,
        'my {NAVIGATION_AID MADE_STUPID}': 50,
        'this {NAVIGATION_AID MADE_STUPID}': 20,
        'this {NAVIGATION_AID MADE_WONDERFUL}': 10,
        'that {NAVIGATION_AID MADE_WONDERFUL}': 30,
        'that {NAVIGATION_AID MADE_STUPID}': 50,
    },
    MADE_STUPID={
        'stupid {}': 30,
        'dumb {}': 10,
        'broken {}': 10,
        'barely usable {}': 10,
        'cheap {}': 10,
    },
    MADE_WONDERFUL={
        '{}': 100,
        'amazing {}': 10,
        'clever {}': 10,
        'perfect {}': 10,
        'capable {}': 5,
        'okay {}': 5,
        'workable {}': 5,
        'decent {}': 10,
        'waterproof {}': 20,
        'crushproof {}': 5,
        'magic {}': 5,
    },
    NAVIGATION_AID={
        'sextant': 10,
        'compass': 10,
        'map': 10,
        'GPS': 10,
        'telescope': 5,
        'cell phone': 5,
        'rope': 5,
        'tent': 5,
        'firestarter': 5,
        'navigation chart': 10,
        'sonar': 5,
        'multitool': 5,
    },
    NAVIGATION_AIDS={
        'maps': 5,
        'binoculars': 10,
        'matches': 1,
        '{NAVIGATION_AID PLURALIZED}': 30,
    },
    THESE_WORTHLESS_TRINKETS={
        '{RANDOM_COUNT} {WORTHLESS_TRINKETS}{AND_MORE}': 15,
        'these {RANDOM_COUNT} {WORTHLESS_TRINKETS}{AND_MORE}': 3,
        'those {RANDOM_COUNT} {WORTHLESS_TRINKETS}{AND_MORE}': 3,
        'some {WORTHLESS_TRINKETS}{AND_MORE}': 10,
        'my {WORTHLESS_TRINKETS}{AND_MORE}': 2,
        'a {WORTHLESS_TRINKET MADE_WORTHLESS}': 10,
        'my {WORTHLESS_TRINKET MADE_WORTHLESS}': 5,
    },
    A_DESIRED_WORTHLESS_TRINKET={
        'a {WORTHLESS_TRINKET}': 10,
    },
    THESE_WORTHLESS_TRINKETS_I_MAYBE_FOUND={
        '{THESE_WORTHLESS_TRINKETS}': 40,
        'these {RANDOM_COUNT} {WORTHLESS_TRINKETS} I found': 10,
        'this {WORTHLESS_TRINKET MADE_WORTHLESS} I found': 10,
    },
    RANDOM_COUNT={
        'two': 10,
        'three': 5,
        'four': 2,
        'five': 1,
    },
    WORTHLESS_TRINKETS={
        '{WORTHLESS_TRINKET PLURALIZED MADE_WORTHLESS}': 10,
        '{WORTHLESS_TRINKET PLURALIZED}': 10,
    },
    AND_MORE={
        '': 2,
        ' and {THESE_WORTHLESS_TRINKETS}': 1,
    },
    WORTHLESS_TRINKET={
        'stamp': 5,
        'eraser': 5,
        'stick': 20,
        'stone': 20,
        'rock': 20,
        'leaf': 20,
        'feather': 10,
        'pebble': 10,
        'tin can': 10,
        'pencil nub': 10,
        'thread': 10,
        'string': 10,
        'bottlecap': 10,
        'marble': 10,
        'fishing line': 5,
        'toy dinosaur': 3,
        'film canister': 3,
        'USB stick': 3,
        'tissue': 1,
        'shell': 1,
        'flower pedal': 1,
        'dead bug': 1,
        'piece of paper': 10,
        'piece of bubblegum': 10,
        'piece of glass': 5,
        'piece of wire': 3,
        'piece of twine': 3,
        'piece of bark': 1,
    },
    MADE_WORTHLESS={
        '{}': 20,
        'fancy {}': 3,
        'pretty {}': 2,
        'plain {}': 4,
        'ordinary {}': 3,
        'ugly {}': 3,
        'hideous {}': 1,
        'colorful {}': 5,
        'precious {}': 1,
        'broken {}': 2,
        'special {}': 2,
        '"special" {}': 2,
        'magic {}': 1,
        'shattered {}': 1,
    }
)


if __name__ == '__main__':
    for i in range(20):
        print(macgyver_sentence())