import tweepy
from config import read_config


CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_KEY = "ACCESS_KEY"
ACCESS_SECRET = "ACCESS_SECRET"


class Keys(object):
    """
    Reads / holds keys required by twitter
    """
    REQUIRED_KEYS = (CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

    def __init__(self, keys_filename):
        """
        Take the filename where you're storing your keys (since you shouldn't do that here.)
        This is just a file that looks like:

                CONSUMER_KEY: dsafsafafsd
                CONSUMER_SECRET: iuhbfusdfiu44
                ACCESS_KEY: vjhbv99889
                ACCESS_SECRET: ivfjslfiguhg98

        """
        with open(keys_filename, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    self.__dict__['_'.join(key.strip().upper().split())] = value.strip()

        missing = 0
        for key in self.REQUIRED_KEYS:
            if key not in self.__dict__:
                print('Missing required key: {}'.format(key))
                missing += 1

        if missing:
            raise RuntimeError('I do not have all required keys')

    @classmethod
    def fix(cls, obj):
        if isinstance(obj, cls):
            return obj
        else:
            return cls(obj)


def bot(keys):
    """
    :param keys: Keys needed for twitter API
    :return: Tweepy API object which can be used (multiple times) to update status, etc.
    """
    keys = Keys.fix(keys)
    auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
    auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
    api = tweepy.API(auth)
    return api