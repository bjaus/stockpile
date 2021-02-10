from .cache import Cache


class MRUCache(Cache):
    """Most Recently Used (MRU) Cache"""

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self._data.move_to_end(key, last=False)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._data.move_to_end(key, last=False)
        return value
