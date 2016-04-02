# maze-builder

Builds mazes, ham-fistedly makes them look interesting and posts them on twitter.

## Requirements

1. Python 3.3+
2. POV-Ray 3.7
3. A twitter account
4. ImageMagick (optional)

## Installation

`make install`
`maze-builder --keys {twitter-key-file} --pov {pov-executable} --include-path {pov-include-paths} -vv`

You can control verbosity with the number of `v`s.  The application will only try to tweet if you provide a key file,
which is formatted like:

                CONSUMER_KEY: dsafsafafsd
                CONSUMER_SECRET: iuhbfusdfiu44
                ACCESS_KEY: vjhbv99889
                ACCESS_SECRET: ivfjslfiguhg98

More command-line options are possible, try `--help` to see them all.

## Development

`make venv`
`. venv/bin/activate`
`python main.py`
