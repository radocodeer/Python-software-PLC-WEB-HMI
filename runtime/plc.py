import time
import os
from dotenv import load_dotenv
from loguru import logger
import json

from runtime.io.modbusMain import ModbusIOThread
from blocks.init.init import init
from runtime.memory.tags import Tags
from runtime.memory.GlobalTags import init_tags as init_global_tags
from runtime.memory.retain import RetainManager
from blocks.OBs.MainOB import MainOB as mainOB

load_dotenv("config/settings.env")


class PLCState:
    STOP = "STOP"
    START = "START"
    WARMUP = "WARMUP"
    RUN = "RUN"
    FAULT = "FAULT"


class SoftPLC:

    def __init__(self):

        logger.add("logs/plc.log", rotation="1 MB", level="INFO")

        self.warmup_timeout = 5.0  # max seconds to wait for I/O ready
        self.start_time = None

        # init optional system layer
        init(self)

        self.state = PLCState.STOP
        self.running = False

        try:
            self.scan_time = float(os.getenv("SCAN_TIME", "0.05"))
        except:
            self.scan_time = 0.05

        #modbus stuff
        self.modbus_io = ModbusIOThread("169.254.167.10")        

        self._clock_start = time.monotonic()

        # memory
        self.tags = Tags()

        logger.info("PLC CORE initialized")
        
    # =========================================================
    # START SEQUENCE
    # =========================================================
    def start(self):

        logger.info("PLC START sequence")

        # 1. build tag structure once
        if not hasattr(self, "_initialized"):
            init_global_tags(self)
            self._initialized = True

        # print tag structure
        #logger.info(json.dumps(self.tags.to_dict(), indent=4))

        # 2. restore retain values BEFORE runtime
        self.load_retain()

        # 3. start Modbus I/O thread and wait for first valid read
        self.modbus_io.start()
        if self.modbus_io.wait_ready(timeout=self.warmup_timeout):
            logger.info("Modbus I/O ready — first read OK")
        else:
            logger.warning("Modbus I/O not ready within timeout — starting anyway")

        # 4. go to RUN state directly (I/O is confirmed ready)
        self.state = PLCState.RUN
        self.running = True

        self._clock_start = time.monotonic()
        self.clock_1hz = False   

        logger.info("PLC → RUN state")

    # =========================================================
    # FIRST SCAN (OB100)
    # =========================================================
    def OB100(self):
        logger.info("FIRST SCAN (OB100) executed")

    # =========================================================
    # STOP
    # =========================================================
    def stop(self):

        self.save_retain()

        # stop Modbus I/O thread (writes 0 to outputs)
        self.modbus_io.stop()

        self.state = PLCState.STOP
        self.running = False

        # SAFE OUTPUT RESET
        self.tags.io.outputs_word = 0        

        logger.info("PLC STOP")

    # =========================================================
    # FAULT
    # =========================================================
    def fault(self, reason="Unknown"):

        self.save_retain()

        # stop Modbus I/O thread (writes 0 to outputs)
        self.modbus_io.stop()

        self.state = PLCState.FAULT
        self.running = False

        # SAFE OUTPUT RESET
        self.tags.io.outputs_word = 0        

        logger.critical(f"PLC FAULT: {reason}")

    # =========================================================
    # I/O HOOKS
    # =========================================================
    def read_inputs(self):
        """Read from fast in-memory buffer (no network call)."""
        inputs = self.modbus_io.get_inputs()
        Dinputs_word = inputs[0]
        Ainputs_word = inputs[1]

        self.tags.io.Dinputs_word = Dinputs_word
        self.tags.io.Ainputs_word = Ainputs_word

        # unpack digitals
        for byte in range(2):
            for bit in range(8):
                value = (Dinputs_word >> (byte * 8 + bit)) & 1
                setattr(self.tags.io, f"i{byte}_{bit}", bool(value))
        

    def write_outputs(self):
        """Write to fast in-memory buffer (no network call)."""
        # pack digitals
        self.tags.io.Doutputs_word = 0        

        for byte in range(2):
            for bit in range(8):
                if getattr(self.tags.io, f"q{byte}_{bit}"):
                    self.tags.io.Doutputs_word |= (1 << (byte * 8 + bit))

        # send both digital and analog arrays
        self.modbus_io.set_outputs([
            self.tags.io.Doutputs_word,
            self.tags.io.Aoutputs_word
        ])
        

    # =========================================================
    # MAIN OB1
    # =========================================================
    def OB1(self):
        mainOB(self)

    # =========================================================
    # CYCLIC RUN LOOP
    # =========================================================
    def run(self):

        logger.info("PLC runtime started")

        try:
            while True:
                
                if self.state in (PLCState.STOP, PLCState.FAULT):
                    time.sleep(0.1)
                    continue

                # START → wait for I/O → RUN (handled in start() now)
                if self.state == PLCState.START:
                    self.state = PLCState.RUN
                    logger.info("PLC → RUN state")

                # =========================
                # RUN MODE
                # =========================
                cycle_start = time.monotonic()

                if self.modbus_io.is_faulted(timeout=0.5):
                    self.fault("I/O Connection Lost (Watchdog Timeout)")
                    continue

                self.clockHandling()

                self.read_inputs()

                try:
                    self.OB1()
                except Exception as e:
                    self.fault(str(e))
                    break
                
                self.write_outputs()

                elapsed = time.monotonic() - cycle_start
                sleep_time = self.scan_time - elapsed

                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    # optional: overload warning
                    logger.warning(f"Scan over time: {elapsed:.4f}s")

        except KeyboardInterrupt:
            logger.warning("CTRL+C → STOP")
            self.stop()

    def clockHandling(self):
        self.update_clock()

    # =========================================================
    # CLOCK Hz
    # =========================================================
    def update_clock(self):
        now = time.monotonic()
        # 500ms toggle
        if now - self._clock_start >= 0.5:
            self._clock_start += 0.5
            self.clock_1hz = not self.clock_1hz

    # =========================================================
    # RETAIN
    # =========================================================
    def save_retain(self):
        RetainManager.save(self.tags)

    def load_retain(self):
        RetainManager.load(self.tags)