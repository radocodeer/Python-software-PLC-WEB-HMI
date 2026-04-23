from blocks.functionsBlocks.increment import IncrementTest
from blocks.functionsBlocks.OneHz import Clock1Hz
from blocks.functionsBlocks.R_TRIG import R_TRIG
from blocks.functionsBlocks.fb_uniCycle_PSA import SimpleSequence

def init(plc):

    plc.clock_1hz = Clock1Hz()
    plc.rtrig = R_TRIG()
    plc.inc = IncrementTest()
    #plc.seq = SimpleSequence()