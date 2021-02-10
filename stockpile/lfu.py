from collections import Counter

from .cache import Cache


class LFUCache(Cache):
    """Lease Frequently Used (LFU) Cache"""

    def __init__(self, maxsize, ttl=None, feeder=None, iterable=False):
        super().__init__(maxsize, ttl=ttl, feeder=feeder, iterable=iterable)
        self._counter = Counter()

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self._counter[key] += 1
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._counter[key] -= 1
        return value

    def __delitem__(self, key):
        super().__delitem__(key)
        del self._counter[key]

    def reset(self):
        super().reset()
        self._counter = Counter()

    def _nextkey(self):
        most_common = self._counter.most_common()
        for key, _ in most_common:
            if key in self:
                del self._counter[key]
                return key, False
            del self._counter[key]
        return None, True
