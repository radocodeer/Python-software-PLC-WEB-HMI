import time
from blocks.functionsBlocks.R_TRIG import R_TRIG
from loguru import logger


class SimpleSequence:

    def __init__(self):
                
        self.rtrig = R_TRIG()

        # clock input
        self.clock_1hz = False

        # step
        self.step = 0
        self.step_next = 0

        # timer (seconds)
        self.timer = 0

        # enable
        self.enable = False

        # 8 digital outputs
        self.q = [False] * 8

    # =========================================================
    def tick(self):
        
        """Call every PLC scan"""

        if not self.enable:
            self.step = 0
            self.step_next = 0
            self.timer = 0
            self.reset_outputs()
            return

        # -------------------------
        # STEP TIMER
        # -------------------------
        if self.timer > 0 and self.rtrig.update(self.clock_1hz):
            self.timer -= 1
            self.debug()

        # -------------------------
        # STEP LOGIC
        # -------------------------
        if self.step == 0:
            # idle
            self.reset_outputs()

            if self.enable:
                self.step_next = 1
                self.timer = 6

        elif self.step == 1:

            self.outputs_pattern_1()

            if self.timer <= 0:
                self.step_next = 2
                self.timer = 6

        elif self.step == 2:

            self.outputs_pattern_2()

            if self.timer <= 0:
                self.step_next = 3
                self.timer = 4

        elif self.step == 3:

            self.outputs_pattern_3()

            if self.timer <= 0:
                self.step_next = 4
                self.timer = 4

        elif self.step == 4:

            self.outputs_pattern_4()

            if self.timer <= 0:
                self.step_next = 0
                self.timer = 2.0

        # -------------------------
        # UPDATE STEP
        # -------------------------
        self.step = self.step_next

    # =========================================================
    # OUTPUT PATTERNS
    # =========================================================
    def reset_outputs(self):
        for i in range(8):
            self.q[i] = False

    def outputs_pattern_1(self):
        self.q = [True, False, False, False, False, False, False, False]

    def outputs_pattern_2(self):
        self.q = [False, True, False, False, False, False, False, False]

    def outputs_pattern_3(self):
        self.q = [False, False, True, False, False, False, False, False]

    def outputs_pattern_4(self):
        self.q = [False, False, False, True, True, False, False, False]

    # =========================================================
    def debug(self):
        logger.info(f"Step: {self.step} | Q: {self.q}")