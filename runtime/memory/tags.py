from runtime.memory.retain import RetainValue

class TagNode:
    """
    Internal node for hierarchical PLC tags
    """
    def __init__(self):
        self._data = {}

    def __getattr__(self, name):

        if name.startswith("_"):
            return super().__getattribute__(name)

        # auto-create nested structure OR return value
        if name not in self._data:
            self._data[name] = TagNode()

        return self._data[name]

    def __setattr__(self, name, value):

        if name == "_data":
            super().__setattr__(name, value)
            return

        # if variable already exists and is retained → update value only
        if name in self._data and isinstance(self._data[name], RetainValue):
            self._data[name].value = value
            return

        # otherwise store normally
        self._data[name] = value

    def to_dict(self, _visited=None):
        if _visited is None:
            _visited = set()

        if id(self) in _visited:
            return "<CIRCULAR_REF>"

        _visited.add(id(self))

        result = {}

        for k, v in self._data.items():

            if isinstance(v, TagNode):
                result[k] = v.to_dict(_visited)

            else:
                if hasattr(v, "value"):
                    result[k] = v.value
                else:
                    result[k] = v

        return result


class Tags:
    """
    PLC-style global tag container (DB root)
    """

    def __init__(self):
        self._root = TagNode()

    def __getattr__(self, name):
        return getattr(self._root, name)

    def __setattr__(self, name, value):

        if name == "_root":
            super().__setattr__(name, value)
        else:
            setattr(self._root, name, value)

    def to_dict(self):
        """
        Flatten full tag structure
        """
        return self._root.to_dict()