class NonRetainTags:

    def __init__(self):
        self.data = {}

    def __getattr__(self, name):
        if name not in self.data:
            self.data[name] = None
        return self.data[name]

    def __setattr__(self, name, value):
        if name == "data":
            super().__setattr__(name, value)
        else:
            self.data[name] = value