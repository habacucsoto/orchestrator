import time
from threading import Thread
from paho.mqtt.publish import single
from store import pond_data

heartbeat_timestamps = {}

def update_heartbeat(id_pond, id_device):
    heartbeat_timestamps[f"{id_pond}/{id_device}"] = time.time()

def monitor_heartbeats():
    while True:
        now = time.time()
        keys = list(heartbeat_timestamps.keys())
        for key in keys:
            last = heartbeat_timestamps.get(key)
            if last is None:
                continue

            # Verificar que el dispositivo aún existe
            id_pond, id_device = key.split("/")
            if id_device not in pond_data.get(id_pond, {}):
                # Eliminar si ya no está en los datos
                heartbeat_timestamps.pop(key, None)
                continue

            if now - last > 15:
                topic = f"aquanest/{key}/heartbeat/error"
                single(topic, "error", hostname="localhost")
        time.sleep(1)