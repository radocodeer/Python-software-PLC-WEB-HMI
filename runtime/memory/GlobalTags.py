from runtime import plc
from runtime.memory.retain import RetainValue

#e.g. 
#RetainValue(0)  # retained
#plc.tags.furnace.pressure = 12.5  # not retained

#Like DBs in TIA
def init_tags(plc):

    for i in range(1, 3):

        motor = getattr(plc.tags, f"motor{i}")

        motor.motor_start = False
        motor.motor_stop = False
        motor.motor_running = False        

        # retained counter
        motor.counter = RetainValue(0)

    plc.tags.furnace.pressure = 12.5
    plc.tags.furnace.startstop = False

    # system retained clock
    plc.tags.system.clock_1hz_last = RetainValue(0)

    plc.tags.system.clock_1hz = False

    #sim
    plc.tags.sim.enable = RetainValue(False)
    plc.tags.sim.pressure = RetainValue(0.0)

    #PSA
    plc.tags.psa.enable = RetainValue(False)
    plc.tags.psa.intSeqCounter = 0

    #digital io    
    for byte in range(2):
        for bit in range(8):
            setattr(plc.tags.io, f"i{byte}_{bit}", False)
            setattr(plc.tags.io, f"q{byte}_{bit}", False)
           
    plc.tags.io.Dinputs_word = 0
    plc.tags.io.Doutputs_word = 0

    #analog io     
    plc.tags.io.Ainputs_word = 0
    plc.tags.io.Aoutputs_word = 65535