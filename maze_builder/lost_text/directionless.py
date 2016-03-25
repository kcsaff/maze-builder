from maze_builder.sewer import MadLibs, Choice
from maze_builder.lost_text.text_decorations import fix_sentence, strike

directionless_sentence = MadLibs({
        '{DIRECTION LOOKING FIXED}': 8,
        '{DIRECTION LOOKING FIXED STRUCK}': 2,
    },
    STRUCK=strike,
    FIXED=fix_sentence,
    DIRECTION={
        'north': 20,
        'south': 20,
        'east': 20,
        'west': 20,
        'true north': 1,
        'true south': 1,
        'true east': 1,
        'true west': 1,
        'up': 5,
        'down': 5,
        'around': 5,
        'forward': 5,
        'back': 5,
        'backward': 1,
        'over': 5,
        'under': 5,
        'through': 5,
        'out': 5,
        'in': 5,
        'left': 2,
        'right': 2,
        'sunwise': 1,
        'sunward': 2,
        'leeward': 2,
        'windward': 2,
        'clockwise': 5,
        'counter-clockwise': 5,
        'widdershins': 1,
        'out of here': 1,
    },
    LOOKING={ # North, south, up, down, etc.
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
)
