import time, requests
from consts import HEARTBEAT_FREQUENCY_SECONDS, DRI_SENSOR_ID, AEROTRACKER_HEARTBEAT_ENDPOINT, MR_FUSION_HEARTBEAT_ENDPOINT

# This loop sends periodic heartbeats to AeroTracker so we know it's online
def heartbeat_loop(logger, last_heartbeat):

    while True:
        time.sleep(HEARTBEAT_FREQUENCY_SECONDS)

        if AEROTRACKER_HEARTBEAT_ENDPOINT != "":
            logger.info("[postHeartbeat] - Sending heartbeat to AeroTracker...")
            if last_heartbeat[0] > time.time() - 30:
                postHeartbeat(logger, AEROTRACKER_HEARTBEAT_ENDPOINT, DRI_SENSOR_ID)

        if MR_FUSION_HEARTBEAT_ENDPOINT != "":
            logger.info("[postHeartbeat] - Sending heartbeat to Mr.Fusion...")
            if last_heartbeat[0] > time.time() - 30:
                postHeartbeat(logger, MR_FUSION_HEARTBEAT_ENDPOINT, DRI_SENSOR_ID)

def postHeartbeat(logger, endpoint, sensor_id):
    heartbeat_json = {
        "time": int(time.time() * 1000),
        "sensor-id": sensor_id,
    }

    logger.debug(f"[postHeartbeat] - heartbeat_json: {heartbeat_json}")

    try:
        logger.info(f"[postHeartbeat] - Sending heartbeat data to {endpoint}...")
        response_from_cloud = requests.request(
            "POST",
            endpoint,
            headers = {
                "Content-Type": "application/json"
            },
            json = heartbeat_json
        )

        if response_from_cloud.status_code == 201:
            logger.info(f"[postHeartbeat] - Successfully sent heartbeat data to Mr.Fusion! Response: {response_from_cloud}")
            return

        logger.critical(f"[postHeartbeat] - Unexpected response when sending heartbeat data to server: {response_from_cloud.text}")

    except Exception as err:
        logger.critical(f"[postHeartbeat] - Error sending heartbeat data to server: {err}")