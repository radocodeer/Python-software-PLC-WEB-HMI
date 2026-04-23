from pymodbus.client import ModbusTcpClient
from loguru import logger
import time


class ModbusReader:

    def __init__(self, ip, port=502):

        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(ip, port=port)

        self.connect()

    def connect(self):

        if self.client.connect():
            logger.info(f"Connected to Modbus server at {self.ip}:{self.port}")
            return True
        else:
            logger.error("Modbus connection failed")
            return False

    def read_inputs_word(self):

        try:

            result = self.client.read_holding_registers(
                address=0,
                count=1
            )

            if result.isError():
                logger.error("Modbus read error")
                return None

            value = result.registers[0]

            logger.info(f"InputsWord = {value:#018b} ({value})")

            return value

        except Exception as e:
            logger.error(f"Read exception: {e}")
            return None


# =========================
# TEST LOOP
# =========================
if __name__ == "__main__":

    IP = "169.254.167.10"   # <-- change to your S7-1200 IP

    reader = ModbusReader(IP)

    while True:

        value = reader.read_inputs_word()

        time.sleep(1)