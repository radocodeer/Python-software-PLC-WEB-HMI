import threading
import uvicorn
from loguru import logger

from runtime.plc import SoftPLC
#from hmi.hmi import PLC_HMI
from webServer.web_server import app, set_plc


def main():

    # =========================
    # CREATE PLC
    # =========================
    plc = SoftPLC()
    #plc.start()
    # =========================
    # INJECT INTO WEB SERVER
    # =========================
    set_plc(plc)
    logger.info("PLC State is: " + plc.state)

    # =========================
    # START PLC THREAD (DAEMON)
    # =========================
    plc_thread = threading.Thread(target=plc.run, daemon=True)
    plc_thread.start()

    # =========================
    # START WEB SERVER (IN THREAD)
    # =========================
    web_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=8000),
        daemon=True
    )
    web_thread.start()

    # =========================
    # START DESKTOP HMI
    # =========================
    #PLC_HMI(plc)

    # =========================
    # KEEP MAIN ALIVE
    # =========================
    try:
        while True:
            pass
    except KeyboardInterrupt:
        plc.stop()


if __name__ == "__main__":
    main()