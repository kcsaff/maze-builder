from maze_builder.sewer import MadLibs, Choice
from maze_builder.lost_text.text_decorations import strike, fix_sentence, pluralize


lost_sentence = MadLibs({
        '{SENTENCE FIXED}': 75,
        '{SENTENCE FIXED STRUCK}': 25
    },
    STRUCK=strike,
    FIXED=fix_sentence,
    PLURALIZED=pluralize,
    GOING={
        'going': 1,
        'traveling': 1,
        'walking': 1,
    },
    IMPOSSIBLE={
        'impossible': 3,
        'futile': 3,
        'hopeless': 3,
        'not possible': 1,
        'absurd': 1,
        'taking so long': 1,
        'so {DIFFICULT}': 5,
    },
    GUESSING={
        'guessing': 10,
        '{GOING} {RANDOMLY}': 10,
    },
    RANDOMLY={
        'randomly': 10,
        'any which way': 10,
        'at random': 10,
        'haphazardly': 5,
    },
    NOW={
        'now': 1,
        'these days': 1,
        'lately': 1,
        'at this point': 1,
    },
    DIFFICULT={
        'difficult': 10,
        'hard': 10,
    },
    IN_ONE_PIECE={
        'in one piece': 10,
        'alive': 10,
        'in my right mind': 10
    },
    THIS_WAY={
        'this way': 10,
        'one way': 10,
    },
    ANOTHER={
        'another': 10,
        'any other': 10,
        'any': 10,
    },
    EVERY_OTHER={
        'every other': 10,
        'any other': 10,
        'all the others': 10,
    },
    REASONABLE={
        'good': 10,
        'reasonable': 10,
        'likely': 10,
    },
    SLIDING={
        'sliding': 10,
        'moving': 10,
        'rotating': 10,
        'mocking me': 10,
        'rising': 5,
        'falling': 5,
    },
    MAZE_PARTS={
        'walls': 30,
        'doors': 10,
        'ceilings': 5,
        'floors': 5,
    },
    FEAR={
        'fear': 10,
        'feel': 10,
        'think': 10,
        'guess': 10,
        'worry': 10,
    },
    DETERMINE={
        'determine': 10,
        'guess': 10,
        'know': 10,
    },
    FOREVER={
        'forever': 10,
        'all my life': 10,
        'endlessly': 10,
    },
    WHICH_WAY={
        'which way': 10,
        'where': 10,
    },
    IMAGINE={
        'imagine': 10,
        'hallucinate': 10,
    },
    MEANT_TO={
        'meant to': 10,
        'intended to': 10,
        'supposed to': 10,
        'going to': 10,
        'to': 10,
    },
    IT_IS={
        'it is': 10,
        'it\'s': 10,
        'it\'s totally': 10,
    },
    I_CANT={
        'I can\'t': 10,
        'I cannot': 10,
        'I don\'t think I can': 10,
        'I {FEAR} I can\'t': 10,
    },
    THIS_IS={
        'this is': 10,
        'that is': 10,
        'that\'s': 10,
    },
    THIS_IS_NOT={
        '{THIS_IS} not': 10,
        'none of {THIS_IS}': 10,
    },
    MAP={
        'map': 20,
        'guidebook': 10,
    },
    THE_MAP={
        'the {MAP}': 10,
        'my {MAP}': 10,
    },
    CARES_ABOUT={
        'cares about': 10,
        'thinks about': 10,
        'remembers': 10,
        'loves': 10,
    },
    STILL_CARES_ABOUT={
        '{CARES_ABOUT}': 10,
        'still {CARES_ABOUT}': 10,
        'would recognize': 5,
    },
    PASSAGE={
        'passage': 15,
        'hallway': 10,
        'hall': 5,
        'exit': 5,
    },
    ALIKE_OR_DIFFERENT={
        'alike': 10,
        'different': 10,
    },
    CALLED={
        'called': 10,
        'screamed': 10,
        'yelled': 10,
    },
    ME={
        'me': 50,
        'this lost explorer': 10,
        'this lost soul': 10,
    },
    SENTENCE={
        "Am I {GOING} in circles?": 1,
        "{IT_IS} {IMPOSSIBLE} to {DETERMINE} which way to go.": 1,
        "I'm just {GUESSING} {NOW}.": 1,
        "{THIS_WAY}'s as {REASONABLE} as {ANOTHER}.": 1,
        "{IT_IS} unmappable.": 1,
        "Are the {MAZE_PARTS}... {SLIDING}?": 1,
        "I {IMAGINE} the {MAZE_PARTS} {SLIDING}.": 1,
        "How am I {MEANT_TO} solve this?": 1,
        "If only someone could point the way.": 1,
        "I hope I don't die here.": 1,
        "This was a mistake.": 1,
        "Here again?": 1,
        "I remember a time before all this...": 1,
        "There's just no way!": 1,
        "Every place is like {EVERY_OTHER}.": 1,
        "I'm in a maze of twisty little {PASSAGE PLURALIZED}, all {ALIKE_OR_DIFFERENT}.": 0.2,
        "Am I even making progress?": 1,
        "Will I get out {IN_ONE_PIECE}?": 1,
        "Is it still possible to escape?": 1,
        "{WHICH_WAY} did I even come from?": 1,
        "{WHICH_WAY} did I come from?": 1,
        "{WHICH_WAY} am I {GOING}?": 1,
        "{WHICH_WAY} should I go?": 1,
        "Taking some time to find my bearings.": 1,
        "{THIS_IS} {IMPOSSIBLE}.": 2,
        "I've tried so hard.": 1,
        "{I_CANT} believe this.": 1,
        "{I_CANT} understand it.": 1,
        "I don't get it.": 1,
        "Is this progress?": 1,
        "Off {THE_MAP}.": 1,
        "{THIS_IS_NOT} on {THE_MAP}!": 1,
        "Ask for directions? I wish I could.": 1,
        "I {FEAR} I've been here {FOREVER}.": 1,
        "I {FEAR} I'll be here {FOREVER}.": 1,
        "I {FEAR} no one {STILL_CARES_ABOUT} {ME}.": 1,
        "I wonder if anyone {STILL_CARES_ABOUT} {ME}.": 1,
        "I {CALLED} down each {PASSAGE} -- but got no response.": 1,
    }
)


if __name__ == '__main__':
    for i in range(20):
        print(lost_sentence())