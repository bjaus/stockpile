from random import choice

from .cache import Cache


class RRCache(Cache):
    """Random Replacement (RR) Cache"""

    def _nextkey(self):
        try:
            key = choice(list(self._data))
        except IndexError:
            return None, True
        return key, False
