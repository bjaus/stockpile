from .cache import Cache


class LRUCache(Cache):
    """Lease Recently Used (LRU) Cache"""

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self._data.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._data.move_to_end(key)
        return value
