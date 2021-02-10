from .cache import Cache


class FIFOCache(Cache):
    """First In First Out (FIFO) Cache"""

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._data.move_to_end(key)
