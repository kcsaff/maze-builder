from maze_builder.sewer import Choice, MadLibs, Selector
from maze_builder.lost_text.text_decorations import fix_phrase
import random
import string

DIRECTIONS = Choice({
    ('☝', '☞', '☟', '☜'): 100,
    ('☚', '☛'): 100,
    ('\U0001F446', '\U0001F447', '\U0001F448', '\U0001F449'): 100,
    ('←', '→', '↑', '↓'): 100,
    ('⬅', '➡', '⬆', '⬇'): 10,
    ('⬅', '⬆', '⬇'): 20,
    ('⇠', '⇢', '⇡', '⇣'): 100,
})

PUNCTUATION = Choice({
    ' ': 100,
    ': ': 100,
    ' - ': 100,
    ' -- ': 100,
    '—': 100,
    ' – ': 100,
    ' : ': 100,
})

def initials():
    L = 2 if random.random() < 0.4 else 3
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(L)).upper()

route_phrase = MadLibs(
    '{ROUTE FIXED}',
    FIXED=fix_phrase,
    INITIALS=Selector.bless(initials),
    ROUTE={
        '{A_DOOR}': 100,
        '{A_ROOM}': 100,
        '{A_HALL}': 100,
    },
    UNVISITED={
        'new': 10,
        'unvisited': 100,
        'unmarked': 10,
        'unmapped': 10,
        'unremembered': 10,
    },
    A_DOOR={
        '{A_}{DOOR}': 100,
        '{A_}{UNVISITED} {DOOR}': 100,
        '{A_}{LOCKED} {DOOR}': 100,
        '{A_}{DOOR}, {WHICH_IS_LOCKED}': 100,
        '{A_}{PRETTY} {DOOR}, {WHICH_IS_LOCKED}': 100,
        '{A_}{PRETTY} {DOOR}': 100,
        '{A_}{LOCKED} {DOOR}, {WHICH_IS_PRETTY}': 20,
        '{A_}{DOOR}, {WHICH_IS_PRETTY}': 20,
    },
    DOOR={
        'door': 500,
        'gate': 100,
        'exit': 50,
    },
    PRETTY={
        'pretty': 20,
        'engraved': 20,
        'red': 10,
        'blue': 10,
        'green': 10,
        'yellow': 10,
        'orange': 10,
        'purple': 20,
        'wood': 50,
        'oak': 10,
        'spruce': 10,
        'pine': 10,
        'steel': 50,
        'bronze': 20,
        'brass': 20,
        'diamond': 10,
        'illustrated': 10,
        'adamantium': 10,
    },
    CARVED={
        'carved': 100,
        'engraved': 100,
    },
    WHICH={
        'which': 100,
        'that': 100,
    },
    WHICH_IS={
        '{WHICH} is': 100,
        'that\'s': 50,
        '{WHICH} has been': 100,
        'that\'s been': 50,
    },
    WHICH_IS_PRETTY={
        '{WHICH_IS} {PRETTY}': 10,
        '{CARVED} "{INITIALS}"': 100,
        '{WHICH} looks out of place': 10,
    },
    LOCKED={
        'locked': 100,
        'bolted': 100,
        'fastened': 100,
        'secured': 100,
        'padlocked': 100,
        'latched': 100,
        'chained': 100,
        'magically sealed': 100,
        'imaginary': 50,
    },
    WHICH_IS_LOCKED={
        '{WHICH_IS} {LOCKED}': 100,
        '{WHICH_IS} {LOCKED} from the other side': 100,
        '{LOCKED} from the other side': 100,
        '{BEYOND_WHICH_IS} {A_MONSTER}': 100,
        '{BEYOND_WHICH_ARE} {MONSTERS}': 100,
        '{BEYOND_WHICH_IS} {A_LADY} or {A_TIGER}': 100,
    },
    BEYOND_WHICH_IS={
        'beyond which is': 100,
        'through which I can {HEAR}': 20,
    },
    BEYOND_WHICH_ARE={
        'beyond which are': 100,
        'through which I can {HEAR}': 20,
    },
    HEAR={
        'hear': 100,
        'just make out': 50,
        'barely see': 50,
    },
    A_MONSTER={
        'my past': 100,
        'my fear': 100,
        'my ex': 50,
        'one possible future': 100,
        'a monster': 100,
        'my former life': 50,
        'my old self': 50,
    },
    A_LADY={
        'a lady': 100,
        'a lover': 100,
        'a prince': 100,
        'a princess': 100,
        'a treasure': 100,
    },
    A_TIGER={
        'a tiger': 100,
        'an executioner': 100,
        'a lion': 50,
        'a bear': 50,
    },
    MONSTERS={
        'my sins': 100,
        'my fears': 100,
        'monsters': 100,
        'many possibilities': 100,
        'the gods': 10,
        'demons': 20,
    },
    A_={
        'a ': 100,
        '': 100,
        'that ': 50,
        'another ': 50,
    },
    A_HALL={
        '{A_}{HALL}': 100,
        '{A_}{UNVISITED} {HALL}': 100,
        '{A_}{FOREBODING} {HALL}': 100,
        '{A_BLOCKADED_HALL}': 100,
    },
    HALL={
        'hall': 100,
        'passage': 100,
        'corridor': 100,
        'tunnel': 100,
        'stairway': 100,
        'cave': 100,
    },
    A_BLOCKADED_HALL={
        '{A_}{BLOCKADED} {HALL}': 100,
        '{A_}{HALL}, {WHICH_IS_BLOCKADED}': 100,
    },
    BLOCKADED={
        'blockaded': 100,
        'barricaded': 100,
        'flooded': 100,
    },
    WHICH_IS_BLOCKADED={
        '{WHICH_IS} {BLOCKADED}': 100,
        'filled with {LOOSE_ROCK}': 100,
    },
    LOOSE_ROCK={
        '{ROCK}': 100,
        'loose {ROCK}': 100,
        'heavy {ROCK}': 10,
    },
    ROCK={
        'rock': 100,
        'dirt': 100,
    },
    FOREBODING={
        'foreboding': 100,
        'dark': 100,
        'pitch-black': 100,
    },
    A_ROOM={
        '{A_}{ROOM}': 100,
        '{A_}{NONDISTINCT} {ROOM}': 50,
        '{A_}{DISTINCT} {ROOM}': 50,
        'the {ROOM} I came from': 10,
    },
    NONDISTINCT={
        'nondistinct': 20,
        'typical': 20,
        'plain': 20,
        'nice': 20,
    },
    DISTINCT={
        'dark': 50,
        'poison-filled': 50,
        'legendary': 20,
    },
    ROOM={
        'room': 50,
        'dead-end': 20,
        'garden': 20,
        'place': 20,
        'area': 20,
        'courtyard': 20,
        'bedroom': 10,
        'kitchen': 10,
        'throne room': 5,
        'treasure room': 5,
        'torture chamber': 5,
        'dungeon': 20,
        'maze': 10,
        'labyrinth': 10,
    }
)


def generate_routes(text='', limit=None):
    directions = list(DIRECTIONS())
    punc = PUNCTUATION()
    random.shuffle(directions)
    parts = [text]
    if limit is not None:
        limit -= len(text)
    for direction in directions:
        part = '\n{}{}{}'.format(direction, punc, route_phrase())
        if limit is not None:
            if len(part) >= limit:
                break
            else:
                limit -= len(part)
        parts.append(part)
    return ''.join(parts).lstrip() + '\n'


if __name__=='__main__':
    for _ in range(20):
        print(generate_routes())
        print('')
