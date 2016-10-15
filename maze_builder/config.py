from argparse import Namespace


def read_config(filename, cls=Namespace, types=dict()):
    d = dict()
    with open(filename, 'r') as f:
        for line in f:
            if line.lstrip()[:1] == '#':
                pass  # comment
            elif ':' in line:
                key, value = line.strip().split(':', 1)
                key = '_'.join(key.strip().split())
                value = value.strip()
                if key in types:
                    value = types[key](value)
                elif value.isdigit():
                    value = int(value)
                elif all(p.isdigit() for p in value.split('.', 1)):
                    value = float(value)
                else:
                    pass  # still a string
                d[key] = value
    return cls(**d)
