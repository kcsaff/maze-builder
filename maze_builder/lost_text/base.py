import re


class TextGenerator(object):
    RE_PATTERN = re.compile(r'\{\s*\w+\s*\}')

    def __call__(self, what):
        if hasattr(what, 'group'):
            what = what.group(0)
        what = what.strip('{}').strip()
        fun = getattr(self, what)
        text = fun() if callable(fun) else fun
        return self.RE_PATTERN.sub(self, text)
