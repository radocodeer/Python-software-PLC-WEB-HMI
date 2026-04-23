class R_TRIG:

    def __init__(self):
        self.prev = False

    def update(self, clk):

        q = clk and not self.prev

        self.prev = clk

        return q