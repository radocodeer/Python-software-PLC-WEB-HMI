class TagNode:

    def __init__(self, name=None, root=None):
        self._name = name
        self._root = root if root else self
        self._data = {}

    def __getattr__(self, name):

        if name.startswith("_"):
            return super().__getattribute__(name)

        if name not in self._data:
            self._data[name] = TagNode(name, self._root)

        return self._data[name]

    def __setattr__(self, name, value):

        if name in ["_name", "_root", "_data"]:
            super().__setattr__(name, value)
        else:
            self._data[name] = value


class TagEngine:

    def __init__(self):
        self.root = TagNode()

    def __getattr__(self, name):
        return getattr(self.root, name)

    def __setattr__(self, name, value):

        if name == "root":
            super().__setattr__(name, value)
        else:
            setattr(self.root, name, value)

    def to_dict(self):
        return self.root._data