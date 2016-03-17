from argparse import Namespace


def read_config(filename, cls=Namespace):
    d = dict()
    with open(filename, 'r') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(':', 1)
                d['_'.join(key.strip().split())] = value.strip()
    return cls(**d)
