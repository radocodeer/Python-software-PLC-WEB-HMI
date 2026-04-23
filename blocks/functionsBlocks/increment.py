from blocks.functionsBlocks.OneHz import Clock1Hz
from blocks.functionsBlocks.R_TRIG import R_TRIG
from loguru import logger


class IncrementTest:

    def __init__(self):
        # FB internal DB (persistent memory)
        self.clock_1hz = Clock1Hz()
        self.rtrig = R_TRIG()

    def increment(self, counter):

        pulse = self.clock_1hz()

        if self.rtrig.update(pulse):

            counter += 1
            logger.info(
                "OB1 executed on R_TRIG (1Hz pulse) "
                + str(counter)
            )

        return counter