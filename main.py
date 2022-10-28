import threading
from consts import *
from driUSBReader import dri_usb_reader_loop
from hearbeat import heartbeat_loop
from logging import logger

last_heartbeat = [0]

try:
    logger.info(
        f"[main] - Starting up with sensor ID {DRI_SENSOR_ID}and sending heartbeats every {HEARTBEAT_FREQUENCY_SECONDS} seconds."
        
    )
    dri_usb_thread = threading.Thread(target=dri_usb_reader_loop, args=(logger,last_heartbeat,))
    dri_usb_thread.start()

    heartbeat_thread = threading.Thread(target=heartbeat_loop, args=(logger,last_heartbeat,))
    heartbeat_thread.start()

except KeyboardInterrupt:
    logger.info("[main] - Shutting down...")