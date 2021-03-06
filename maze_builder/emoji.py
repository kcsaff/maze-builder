import string


HAPPY_FACES = ''.join(
    [chr(x) for x in range(0x1f600, 0x1f608)]
    + [chr(x) for x in range(0x1f609, 0x1f60c)]
    + ['\U0001f60e\u263a\U0001f642\U0001f917\U0001f913\U0001f60c\U0001f61b\U0001f61c\U0001f61d\U0001f643']
    + ['\U0001f911']
)

LOVE_FACES = ''.join(
    ['\U0001f60d\U0001f633']
    + [chr(x) for x in range(0x1f617, 0x1f61b)]
)

NEUTRAL_FACES = ''.join(
    ['\U0001f914\U0001f610\U0001f611\U0001f636\U0001f644\U0001f60f\U0001f62a\U0001f634\U0001f612\U0001f614']
)

SAD_FACES = ''.join(
    ['\U0001f623\u2639\U0001f641\U0001f616\U0001f61e\U0001f622\U0001f62d\U0001f629']
)

SCARED_FACES = ''.join(
    ['\U0001f62e\U0001f910\U0001f625\U0001f62f\U0001f62b\U0001f613\U0001f615\U0001f632\U0001f61f\U0001f627\U0001f628']
    + ['\U0001f630\U0001f631\U0001f635']
)

SICK_FACES = ''.join(
    ['\U0001f637\U0001f912\U0001f915']
)

ANGRY_FACES = ''.join(
    ['\U0001f624\U0001f62c\U0001f621\U0001f620']
)

MONSTER_FACES = ''.join(
    ['\U0001f608\U0001f47f\U0001f479\U0001f47a']
)

DEAD_THINGS = ''.join(
    ['\U0001f480\u2620\U0001f47b']
)

SCIFI_FACES = ''.join(
    ['\U0001f47d\U0001f47e\U0001f916']
)

FEATURE_SETS = {
    string.ascii_uppercase: 100,
    string.digits: 100,
    NEUTRAL_FACES: 100,
    SCARED_FACES: 100,
}
