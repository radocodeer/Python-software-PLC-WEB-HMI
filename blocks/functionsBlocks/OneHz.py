import time


class Clock1Hz:

    def __init__(self):
        self.last_time = time.monotonic()
        self.Q = False

    def __call__(self):

        now = time.monotonic()

        if now - self.last_time >= 0.5:
            self.last_time += 0.5
            self.Q = not self.Q

        return self.Q