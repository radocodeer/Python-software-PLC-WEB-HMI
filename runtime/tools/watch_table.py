class WatchTable:

    def __init__(self, tag_engine):
        self.tags = tag_engine

    def _flatten(self, node, path=""):
        """Convert nested PLC structure into flat view"""

        result = {}

        for key, value in node._data.items():

            full_key = f"{path}.{key}" if path else key

            # if it's another node (object)
            if hasattr(value, "_data"):
                result.update(self._flatten(value, full_key))
            else:
                result[full_key] = value

        return result

    def dump(self):
        """Return all PLC tags in flat format"""
        return self._flatten(self.tags.root)