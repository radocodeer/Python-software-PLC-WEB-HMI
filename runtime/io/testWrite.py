from pymodbus.client import ModbusTcpClient
from loguru import logger


class ModbusWriter:

    def __init__(self, ip, port=502):

        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(ip, port=port)

        self.connect()

        self.last_value = None

    def connect(self):

        if self.client.connect():
            logger.info(f"Modbus connected → {self.ip}:{self.port}")
            return True
        else:
            logger.error("Modbus connection failed")
            return False

    def write_outputs_word(self, value):

        try:
            # reconnect if needed
            if not self.client.connected:
                logger.warning("Modbus reconnecting...")
                self.connect()

            result = self.client.write_register(
                address=1,
                value=value
            )

            if result.isError():
                logger.error("Modbus write error")

        except Exception as e:
            logger.error(f"Write exception: {e}")
# =========================
# TEST LOOP
# =========================
if __name__ == "__main__":

    IP = "169.254.167.10"   # change to your S7-1200 IP

    writer = ModbusWriter(IP)

    value = 0

    while True:

        # simple pattern test (bit toggle)
        value = 65535

        writer.write_outputs_word(value)

        