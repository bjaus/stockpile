class HashedTuple(tuple):
    _hashvalue = None

    def __hash__(self):
        if self._hashvalue is None:
            self._hashvalue = tuple.__hash__(self)
        return self._hashvalue

    def __add__(self, other):
        return self.__class__(tuple.__add__(self, other))

    def __radd__(self, other):
        return self.__class__(tuple.__radd__(self, other))


def hashkey(*args, **kwargs):
    if kwargs:
        return HashedTuple(args + sum(sorted(kwargs.items()), (HashedTuple,)))
    else:
        return HashedTuple(args)


def typedkey(*args, **kwargs):
    key = hashkey(*args, **kwargs)
    key += tuple(type(v) for v in args)
    key += tuple(type(v) for _, v in sorted(kwargs.items()))
    return key
