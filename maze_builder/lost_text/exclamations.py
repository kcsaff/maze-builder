import random
from maze_builder.sewer import Choice


EXCLAMATIONS = Choice({
    ('What', '?.'): 1,
    ('Well', '!.'): 1,
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
    ('Uh-oh', '.!'): 2,
    ('Welp', '.!'): 1,
    ('Yay', '.!'): 1,
    ('Gee', '.!'): 2,
    ('Crikey', '.!'): 1,
    ('Voilà', '.!'): 1,
    ('Argh', '.!'): 1,
    ('Ugh', '.!'): 2,
    ('Ouch', '.!'): 1,
    ('Boom', '!'): 1,
    ('Ew', '!.'): 2,
    ('Ow', '!.'): 1,
    ('Yuck', '!.'): 1,
    ('Dagnabit', '!.'): 1,
    ('Blimey', '!.'): 1,
    ('Egads', '!.'): 1,
    ('Crud', '!.'): 1,
    ('Why', '!.?'): 2,
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
    ('Aha', '!.'): 2,
    ('Bother', '!.'): 1,
    ('Good grief', '!.'): 1,
    ('What in tarnation', '!.'): 1,
    ('Snap', '!.'): 1,
    ('Bah', '!.'): 1,
    ('Ack', '!.'): 2,
    ('Blast', '!.'): 1,
    ('Oy vey', '!.'): 1,
    ('Uff da', '!.'): 1,
    ('Hey', '!.'): 1,
    ('Shucks', '!.'): 1,
    ('Sheesh', '!.'): 1,
    ('Glorious', '!.'): 1,
})


INVERTED_PUNCTUATION = {
    '?': '¿',
    '!': '¡',
}


def exclaim():
    exclamation, punctuation = EXCLAMATIONS()
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

    return exclamation + punctuation


def exclaim_appending(text):
    return text + ' ' + exclaim()