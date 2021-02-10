__all__ = [
    "cached",
    "cachedmethod",
]


import importlib
from functools import wraps

from .util.keys import hashkey


def pickey(key, *args, **kwargs):
    if len(args) == 1 and not kwargs:
        return args[0]
    return key(*args, **kwargs)


def cached(cache=None, key=hashkey):
    def decorator(func):
        func.cache = cache
        cache.feeder = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            if cache is None or cache.frozen:
                return func(*args, **kwargs)

            k = pickey(key, *args, **kwargs)
            if k not in cache:
                cache[k] = func(*args, **kwargs)
            return cache[k]

        return wrapper

    return decorator


def cachedmethod(cache=None, key=hashkey):
    def decorator(method):
        method.cache = cache
        cache.feeder = method

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if cache is None or cache.frozen:
                return method(self, *args, **kwargs)

            cache.feederobj = self
            k = pickey(key, *args, **kwargs)
            if k not in cache:
                cache[k] = method(self, *args, **kwargs)
            return cache[k]

        return wrapper

    return decorator
