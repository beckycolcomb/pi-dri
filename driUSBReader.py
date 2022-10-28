from consts import DRI_LOG_FILE, DRI_SENSOR_ID, DRI_USB_DEVICE, MR_FUSION_DETECTION_ENDPOINT, AEROTRACKER_DETECTION_ENDPOINT, DRI_FREQUENCY_SECONDS
import json, serial, requests, os, time
from datetime import datetime


# This loop continuously reads from a USB serial looking for DRI detection data in JSON format.
# It forwards these detections to AeroTracker, and logs them to a CSV file.
def dri_usb_reader_loop(logger, last_heartbeat):
    dri_serial_connection = serial.Serial(DRI_USB_DEVICE, 115200, timeout=1)
    dri_serial_connection.flush()

    dri_log_file_is_new = not os.path.exists('/home/pi/'+ DRI_LOG_FILE)
    if dri_log_file_is_new:
        dri_log_titles = ["BST Datetime", "Drone_ID", "Confidence_level", "Bearing", "MAC_address", 
         "Drone_latitude", "Drone_longitude", "Drone_height", "Drone_speed"]
        with open(DRI_LOG_FILE, "a+") as dri_log_file:
            dri_log_file.write(",".join(dri_log_titles))
            dri_log_file.write("\n")

    while True:
        time.sleep(DRI_FREQUENCY_SECONDS)
        bytes_from_dri_serial = dri_serial_connection.readline().decode('utf-8', errors="ignore").rstrip()

        # If we don't get any bytes from serial, there's nothing to do, so just continue...
        if not bytes_from_dri_serial:
            continue

        dri_detection = json.loads(bytes_from_dri_serial).get('data',{})

        # If the detection is just an empty JSON object, we can't do anything with it, so just continue...
        if dri_detection == {}:
            if json.loads(bytes_from_dri_serial).get('sensor-id', {}) != {}:
                last_heartbeat[0] = time.time()
                continue
            else:
                continue

        if AEROTRACKER_DETECTION_ENDPOINT != "":
            logger.info("[dri_usb_reader_loop] - Sending detection to AeroTracker...")
            postDetection(logger, dri_detection, AEROTRACKER_DETECTION_ENDPOINT)

        if MR_FUSION_DETECTION_ENDPOINT != "":
            logger.info("[dri_usb_reader_loop] - Sending detection to Mr.Fusion...")
            postDetection(logger, dri_detection, MR_FUSION_DETECTION_ENDPOINT)

        # After everything has been taken care of for this detection, we add it to our detection log.
        detections_log_row = [
            datetime.now().isoformat(),
            dri_detection.get('drone',{}).get('drone_id',"PLACEHOLDER_DRONE_ID"),
            1, # confidence_level
            float(dri_detection.get('drone',{}).get('bearing',0)) % 360,
            dri_detection.get('drone',{}).get('mac_address',"PLACEHOLDER_MAC_ADDRESS"),      
            dri_detection.get('drone',{}).get('latitude',0),
            dri_detection.get('drone',{}).get('longitude',0),
            dri_detection.get('drone',{}).get('height',0),
            dri_detection.get('drone',{}).get('speed',0)
        ]
        with open(DRI_LOG_FILE, "a+") as dri_log_file:
          dri_log_file.write(",".join([str(v) for v in detections_log_row]) + "\n")


def postDetection(logger, dri_detection, endpoint):
    try:
        r = requests.post(
            endpoint,
            json={
                "time": int(time.time() * 1000),
                "sensor-id": DRI_SENSOR_ID,
                "position": {
                    "latitude": float(dri_detection.get('drone',{}).get('latitude',0)),
                    "longitude": float(dri_detection.get('drone',{}).get('longitude',0)),
                    "altitude": float(dri_detection.get('drone',{}).get('height',0)), #In DRI, the barometric altitude is "height".
                    "accuracy": 1.0, # +/- meters
                    "speed-horizontal": float(dri_detection.get('drone',{}).get('speed',0)),
                    "bearing": float(dri_detection.get('drone',{}).get('bearing',0)) % 360
                },
                "metadata": [
                    {
                        "key": "type",
                        "val": "drone"
                    },{
                        "key": "mac_address",
                        "val": str(dri_detection.get('drone',{}).get('mac_address',"PLACEHOLDER_MAC_ADDRESS")),
                        "type": "primary"
                    },{
                        "key": "source",
                        "val": str(dri_detection.get('drone',{}).get('mac_address',"PLACEHOLDER_MAC_ADDRESS")),
                        "type": "primary"
                    },{
                        "key": "runtime",
                        "val": str(dri_detection.get('sensor',{}).get('runtime',0)),
                        "type": "primary"
                    },{
                        "key": "registration",
                        "val": str(dri_detection.get('drone',{}).get('drone_id',"PLACEHOLDER_DRONE_ID")),
                        "type": "primary"
                    },{
                        "key": "icao",
                        "val": str(dri_detection.get('drone',{}).get('drone_id',"PLACEHOLDER_DRONE_ID")),
                        "type": "primary"
                    },{
                        "key": "Operator Location",
                        "val": f"%d, %d" % (float(dri_detection.get('base',{}).get('latitude',0)), float(dri_detection.get('base',{}).get('longitude',0))),
                        "type": "volatile"
                    },{
                        "key": "alt",
                        "val": str(dri_detection.get('drone',{}).get('altitude',0)),
                        "type": "volatile"
                    }
                ]
            },
            timeout=1.0
        )
        logger.debug(f"[postDetection] - response from {endpoint}: {r.text}")
    except Exception as e:
        logger.critical(f"[postDetection] - Error when forwarding dri packet to server: {e}")