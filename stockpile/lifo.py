from .cache import Cache


class LIFOCache(Cache):
    """Last In First Out (LIFO) Cache"""

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._data.move_to_end(key, last=False)
