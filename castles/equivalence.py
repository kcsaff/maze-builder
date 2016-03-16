
class Equivalence(object):
    def __init__(self, *values):
        self._canon = None
        self._values = set(values)

    @property
    def canon(self):
        if self._canon is None:
            return self
        else:
            self._canon = self._canon.canon
            return self._canon

    def values(self):
        return self.canon._values

    def __eq__(self, other):
        return other is not None and self.canon is other.canon

    def __ne__(self, other):
        return other is None or self.canon is not other.canon

    def join(self, other):
        if self.canon is not other.canon:
            # Update other
            other.canon._values.update(self.canon._values)
            # Clear self
            self.canon._values = None
            # Update self
            self.canon._canon = other.canon