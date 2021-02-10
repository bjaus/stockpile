__all_ = ["Link"]


class Link:
    __slots__ = ("key", "expire", "next", "prev")

    def __init__(self, key=None, expire=None):
        self.key = key
        self.expire = expire

    def onlink(self, root, expire):
        self.expire = expire
        self.next = root
        self.prev = root.prev
        self.prev.next = root.prev = self

    def unlink(self):
        self.prev.next, self.next.prev = self.next, self.prev

    @classmethod
    def setroot(cls):
        link = cls()
        link.prev = link.next = link
        return link
