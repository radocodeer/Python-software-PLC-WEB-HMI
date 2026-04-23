from pymodbus.client import ModbusTcpClient
from loguru import logger
import threading
import time


class ModbusReadWrite:

    def __init__(self, ip, port=502):

        self.client = ModbusTcpClient(ip, port=port)

        if self.client.connect():
            logger.info(f"Connected to S7-1200 Modbus server at {ip}")
        else:
            logger.error("Modbus connection failed")

    def read_inputs(self, start_addr=0, count=2):

        try:

            result = self.client.read_holding_registers(
                address=start_addr,
                count=count
            )

            if result.isError():
                logger.error("Modbus read error")
                return None

            # return array of registers
            return result.registers

        except Exception as e:
            logger.error(f"Read exception: {e}")
            return None
        
    def write_outputs(self, values, start_addr=2):

        try:
            # reconnect if needed
            is_connected = False
            if hasattr(self.client, 'connected'):
                is_connected = self.client.connected
            elif hasattr(self.client, 'is_socket_open'):
                is_connected = self.client.is_socket_open()

            if not is_connected:
                logger.warning("Modbus reconnecting...")
                self.client.connect()

            result = self.client.write_registers(
                address=start_addr,
                values=values
            )

            if result.isError():
                logger.error("Modbus write error")
                return False
            return True

        except Exception as e:
            logger.error(f"Write exception: {e}")
            return False

    def close(self):
        self.client.close()


# =========================================================
# THREADED MODBUS I/O  (decouples network from PLC scan)
# =========================================================
class ModbusIOThread:
    """
    Runs Modbus read/write in a separate daemon thread.
    The PLC scan loop reads/writes to shared buffers (instant),
    while this thread handles the slow network I/O independently.
    """

    def __init__(self, ip, port=502, poll_interval=0.05):

        self._modbus = ModbusReadWrite(ip, port)
        self._poll_interval = poll_interval

        # shared I/O buffers (lists of ints)
        self._lock = threading.Lock()
        self._input_words = [0, 0]       # [Digital In, Analog In]
        self._output_words = [0, 0]      # [Digital Out, Analog Out]

        self._running = False
        self._thread = None
        self._ready = threading.Event()  # set after first successful read
        self._last_success_time = time.monotonic()

    # ----- buffer access (called by PLC scan — instant) -----

    def get_inputs(self):
        """Read latest input array from buffer (no network call)."""
        with self._lock:
            return list(self._input_words)

    def set_outputs(self, values):
        """Write output array to buffer (no network call)."""
        with self._lock:
            self._output_words = list(values)

    def wait_ready(self, timeout=5.0):
        """Block until first successful I/O cycle completes."""
        return self._ready.wait(timeout=timeout)

    def is_faulted(self, timeout=0.5):
        """Returns True if no successful I/O occurred within the timeout."""
        if not self._ready.is_set():
            return False  # Don't fault during initial startup wait
        return (time.monotonic() - self._last_success_time) > timeout

    # ----- thread lifecycle -----

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._io_loop, daemon=True)
        self._thread.start()
        logger.info("Modbus I/O thread started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        # safe state: write 0s to outputs
        try:
            self._modbus.write_outputs([0, 0], start_addr=2)
        except Exception:
            pass
        logger.info("Modbus I/O thread stopped")

    # ----- background loop -----

    def _io_loop(self):
        while self._running:
            try:
                # READ inputs from hardware (Address 0, count 2)
                read_vals = self._modbus.read_inputs(start_addr=0, count=2)
                read_ok = read_vals is not None

                if read_ok:
                    with self._lock:
                        self._input_words = read_vals
                    # signal that we have valid data
                    if not self._ready.is_set():
                        self._ready.set()

                # WRITE outputs to hardware (Address 2)
                with self._lock:
                    out = list(self._output_words)
                write_ok = self._modbus.write_outputs(out, start_addr=2)

                if read_ok and write_ok:
                    self._last_success_time = time.monotonic()

            except Exception as e:
                logger.error(f"Modbus I/O thread error: {e}")

            time.sleep(self._poll_interval)


# =========================
# TEST LOOP
# =========================

# if __name__ == "__main__":
    
#     IP = "10.42.199.10"   # change to your S7-1200 IP

#     writerReader = ModbusReadWrite(IP)

#     value1 = 0
#     value2 = 65535

#     while True:           

#         value1 = writerReader.read_inputs_word()                               

#         # simple pattern test (bit toggle)
#         value2 = 65535

#         writerReader.write_outputs_word(value2)

#         time.sleep(0.1)
