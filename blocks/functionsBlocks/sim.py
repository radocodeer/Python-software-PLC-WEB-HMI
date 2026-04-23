from blocks.functionsBlocks.OneHz import Clock1Hz
from blocks.functionsBlocks.R_TRIG import R_TRIG
from loguru import logger
import random


class RandomPressure:

    def __init__(self):
        # =========================
        # STATIC (VAR_STAT like PLC FB)
        # =========================
        self.pressure = 0.0

        # FB internal instances
        self.clock_1hz = Clock1Hz()
        self.rtrig = R_TRIG()

    def update(self, enable):

        pulse = self.clock_1hz()

        # =========================
        # ENABLE CHECK
        # =========================
        if not enable:
            if self.rtrig.update(pulse):
                logger.info("Function not enabled!")
                #return self.pressure  # keep last value (PLC behavior)

        # =========================
        # 1Hz trigger
        # =========================
        if self.rtrig.update(pulse):

            self.pressure = random.uniform(0.0, 100.0)
            logger.debug("pressure updated to: " + str(self.pressure))

        return self.pressure