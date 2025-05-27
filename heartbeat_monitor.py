import time
from threading import Lock
from mqtt_client import client  
from store import pond_data

heartbeat_timestamps = {}
lock = Lock()

def update_heartbeat(id_pond, id_device):
    with lock:
        heartbeat_timestamps[f"{id_pond}/{id_device}"] = time.time()

def monitor_heartbeats():
    while True:
        now = time.time()
        with lock:
            keys = list(heartbeat_timestamps.keys())

        for key in keys:
            last = heartbeat_timestamps.get(key)
            if last is None:
                continue

            diferencia = now - last

            id_pond, id_device = key.split("/")
            sensores = pond_data.get(id_pond, {})

            tipo_dispositivo = None 

            for sensor_id, sensor_data in sensores.items():
                if id_device == sensor_id:
                    tipo_dispositivo = "sensor"
                    break
                if id_device in sensor_data.get("actuators", {}):
                    tipo_dispositivo = "actuator"
                    break

            if tipo_dispositivo is None:
                if diferencia > 5:
                    topic = f"aquanest/{id_pond}/{id_device}/heartbeat/error"
                    client.publish(topic, "error")
                    with lock:
                        heartbeat_timestamps.pop(key, None)
                continue

            if diferencia > 5:
                topic = f"aquanest/{id_pond}/{id_device}/heartbeat/error"
                client.publish(topic, "error")
                with lock:
                    heartbeat_timestamps.pop(key, None)
        time.sleep(1)