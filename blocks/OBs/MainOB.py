from loguru import logger
from blocks.functionsBlocks.increment import IncrementTest
from blocks.functionsBlocks.sim import RandomPressure
from blocks.functionsBlocks.R_TRIG import R_TRIG
from blocks.functionsBlocks.fb_uniCycle_PSA import SimpleSequence

inc = IncrementTest()
sim = RandomPressure() 

rtrig = R_TRIG()
seq = SimpleSequence()

def logit(plc):
        pulse = plc.clock_1hz
        if rtrig.update(pulse):
            logger.info(f"plc.tags.sim.pressure {plc.tags.sim.pressure}")

def blinking_outputs(plc):

    if plc.clock_1hz:
        logger.debug("ON")
        for byte in range(2):
            for bit in range(8):
                setattr(plc.tags.io, f"q{byte}_{bit}", True)
    else:
        logger.debug("OFF")
        for byte in range(2):
            for bit in range(8):
                setattr(plc.tags.io, f"q{byte}_{bit}", False)                    

def seq_PSA(plc):
    #in
    seq.clock_1hz = plc.clock_1hz
    seq.enable = plc.tags.psa.enable
    #function
    seq.tick()
    #valves
    plc.tags.io.q1_0 = seq.q[0]
    plc.tags.io.q1_1 = seq.q[1]
    plc.tags.io.q1_2 = seq.q[2]
    plc.tags.io.q1_3 = seq.q[3]
    plc.tags.io.q1_4 = seq.q[4]
    plc.tags.io.q1_5 = seq.q[5]
    plc.tags.io.q1_6 = seq.q[6]
    plc.tags.io.q1_7 = seq.q[7]
    #for HMI
    plc.tags.psa.intSeqCounter = seq.timer
    


def MainOB(plc):
    pass
    #plc.tags.motor1.counter = inc.increment(plc.tags.motor1.counter)
    if plc.tags.sim.enable:
        plc.tags.sim.pressure = sim.update(plc.tags.sim.enable)   

    seq_PSA(plc)
    
    #blinking_outputs(plc)

    #log each 1 sec
    #logit(plc)
    
                