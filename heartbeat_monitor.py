import time
from threading import Thread
from paho.mqtt.publish import single

heartbeat_timestamps = {}

def update_heartbeat(id_pond, id_device):
    heartbeat_timestamps[f"{id_pond}/{id_device}"] = time.time()

def monitor_heartbeats():
    while True:
        now = time.time()
        for key, last in heartbeat_timestamps.items():
            if now - last > 15:  # más de 2 segundos sin latido
                if "sensor" in key:
                    topic = f"aquanest/{key}/heartbeat/error"
                else:
                    topic = f"aquanest/{key}/heartbeat/error"
                single(topic, "error", hostname="localhost")
        time.sleep(1)
