__all__ = ["CacheError"]


from time import monotonic
from collections.abc import MutableMapping
from collections import OrderedDict

from .util.link import Link


class CacheError(Exception):
    pass


class Cache(MutableMapping):
    """Base Cache with per-item Time-To-Live (TTL)"""

    def __init__(self, maxsize, ttl=None, feeder=None, feederobj=None, iterable=False):
        self.reset()
        self.ttl = ttl
        self.unfreeze()
        self.feeder = feeder
        self.maxsize = maxsize
        self.iterable = iterable
        self.freederobj = feederobj

    def __repr__(self):
        return "{}(size={:,} maxsize={:,} ttl={} hits={:,} misses={})".format(
            self.__class__.__name__,
            self.size,
            self.maxsize,
            f"{self.ttl:,}" if self.ttl else "'off'",
            0,
            0,
        )

    def __setitem__(self, key, value):
        time = self.timer()
        self.expire(time)
        size = 0 if key in self._data else 1
        if self.ttl:
            link, err = self._linkup(key)
            if err:
                self._links[key] = link = Link(key)
            else:
                link.unlink()
            link.onlink(root=self._root, expire=time + self.ttl)
        self._size += size
        self._data[key] = value
        if self._size > self._maxsize:
            self.popitem()
        return value

    def __getitem__(self, key):
        self.expire()
        if key in self:
            self._hits += 1
            return self._data[key]
        self._misses += 1
        return self.__missin__(key)

    def __delitem__(self, key):
        del self._data[key]
        self._size -= 1
        try:
            link = self._links.pop(key)
        except KeyError:
            pass
        else:
            link.unlink()

    def __contains__(self, key):
        if not self._iterable:
            self.expire()
        if self.ttl:
            link, err = self._linkup(key)
            if err:
                return False
            return link.expire > self.timer()
        return key in self._data

    def __iterable__(self):
        if not self.iterable:
            raise CacheError("set `iterable` to `True` to enable")
        todel = list()
        for key in self._data.keys():
            if key in self:
                yield key
            else:
                todel.append(key)
        for key in todel:
            del self[key]

    def __len__(self):
        return self.size

    def __missing__(self, key):
        if not self.feeder:
            raise KeyError(key)
        try:
            if self.feederobj:
                self[key] = self.feeder(self.feederobj, key)
            else:
                self[key] = self.feeder(key)
        except TypeError:
            raise CacheError(f"feeder rejected key: {key!r}")
        return self._data[key]

    @property
    def feeder(self):
        return self._feeder

    @feeder.setter
    def feeder(self, value):
        if value is None:
            self._feeder = None
        elif hasattr(value, "__call__"):
            self._feeder = value
        else:
            raise CacheError("feeder must be either `None` (off) or function/method")

    @property
    def feederobj(self):
        return self._feederobj

    @feederobj.setter
    def feederobj(self, value):
        self._feederobj = value

    @property
    def frozen(self):
        return self._freeze

    @property
    def hits(self):
        return self._hits

    @property
    def iterable(self):
        self._iterable

    @iterable.setter
    def iterable(self, value):
        self._iterable = bool(value)

    @property
    def maxsize(self):
        return self._maxsize

    @maxsize.setter
    def maxsize(self, value):
        self._maxsize = int(value)
        if self._maxsize < 1:
            raise ValueError("positive integer required: `maxsize`")

    @property
    def misses(self):
        return self._misses

    @property
    def size(self):
        return self._size

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        if value in (None, 0):
            self._ttl = 0
            return
        self._ttl = int(value)
        if self._ttl < 1:
            raise ValueError("positive integer required: `ttl`")

    def expire(self, time=None):
        if not self.ttl:
            return
        if not time:
            time = self.timer()
        curr = self._root.next()
        while curr is not self._root and curr.expire < time:
            nxt = curr.next
            del self[curr.key]
            curr = nxt

    def freeze(self):
        self._freeze = True

    def get(self, key, default=None, feed=False):
        if key in self or feed:
            return self[key]
        return default

    def pop(self, key=None, default=None):
        if key is None:
            key, err = self._nextkey()
            if err:
                raise CacheError("{self.__class__.__name__} is empty")
        if key in self:
            value = self[key]
            del self[key]
            return value
        return default

    def popitem(self, key=None, default=None):
        if key is None:
            key, err = self._nextkey()
            if err:
                raise CacheError("{self.__class__.__name__} is empty")
        if key in self:
            return (key, self.pop(key))
        return (key, default)

    def reset(self):
        self._size = 0
        self._hits = 0
        self._misses = 0
        self._data = OrderedDict()
        self._links = OrderedDict()
        self._root = Link.setroot()

    def set(self, key, value):
        self[key] = value

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default

    def setmany(self, *args):
        for arg in args:
            try:
                key, value = arg
            except ValueError:
                raise CacheError("*args should be `(key, value)` tuples")
            self[key] = value

    def timer(self):
        return monotonic()

    def unfreeze(self):
        self._freeze = False

    def _linkup(self, key):
        try:
            value = self._links[key]
        except KeyError:
            return None, True
        return value, False

    def _nextkey(self):
        try:
            key = next(iter(self._data))
        except (KeyError, StopIteration):
            return None, True
        return key, False
