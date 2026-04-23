import json
from loguru import logger


class RetainValue:

    def __init__(self, value):
        self.value = value
        self.retain = True

    def __repr__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return bool(self.value)

    def __iadd__(self, other):
        self.value += other
        return self

    def __isub__(self, other):
        self.value -= other
        return self

    def __imul__(self, other):
        self.value *= other
        return self

    def __itruediv__(self, other):
        self.value /= other
        return self

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __truediv__(self, other):
        return self.value / other


class RetainManager:

    FILE = "retain.json"

    @staticmethod
    def save(tags):

        retain_data = {}

        def walk(node, path=""):

            for k, v in node._data.items():

                full_path = f"{path}.{k}" if path else k

                if isinstance(v, RetainValue):

                    retain_data[full_path] = v.value
                    #logger.info(f"Saved retained value {k} = {v.value}")

                elif hasattr(v, "_data"):

                    walk(v, full_path)

        walk(tags._root)

        with open(RetainManager.FILE, "w") as f:
            json.dump(retain_data, f, indent=2)

        logger.info("Retain memory saved")


    @staticmethod
    def load(tags):

        try:

            with open(RetainManager.FILE, "r") as f:
                retain_data = json.load(f)

        except FileNotFoundError:

            logger.warning("No retain memory found")
            return

        def walk(node, path=""):

            for k, v in node._data.items():

                full_path = f"{path}.{k}" if path else k

                if isinstance(v, RetainValue):

                    if full_path in retain_data:

                        v.value = retain_data[full_path]
                        #logger.info(f"Loaded retained value {k} = {v.value}")

                elif hasattr(v, "_data"):

                    walk(v, full_path)

        walk(tags._root)

        logger.info("Retain memory restored")