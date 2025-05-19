# import time
# from threading import Thread
# from paho.mqtt.publish import single
# from store import pond_data

# heartbeat_timestamps = {}

# def update_heartbeat(id_pond, id_device):
#     heartbeat_timestamps[f"{id_pond}/{id_device}"] = time.time()

# def monitor_heartbeats():
#     while True:
#         now = time.time()
#         keys = list(heartbeat_timestamps.keys())
#         for key in keys:
#             last = heartbeat_timestamps.get(key)
#             if last is None:
#                 continue

#             # Verificar que el dispositivo aún existe
#             id_pond, id_device = key.split("/")
#             if id_device not in pond_data.get(id_pond, {}):
#                 # Eliminar si ya no está en los datos
#                 heartbeat_timestamps.pop(key, None)
#                 continue

#             if now - last > 15:
#                 topic = f"aquanest/{key}/heartbeat/error"
#                 single(topic, "error", hostname="localhost")
#         time.sleep(1)

import time
from threading import Lock
from mqtt_client import client  # Usar el cliente persistente
from store import pond_data

heartbeat_timestamps = {}
lock = Lock()

def update_heartbeat(id_pond, id_device):
    with lock:
        print(f"[HEARTBEAT RECIBIDO] {id_pond}/{id_device}")
        heartbeat_timestamps[f"{id_pond}/{id_device}"] = time.time()

def monitor_heartbeats():
    print("[MONITOR] Iniciando monitoreo de heartbeats...")
    while True:
        now = time.time()
        with lock:
            keys = list(heartbeat_timestamps.keys())
        
        print(f"[MONITOR] Revisión de {len(keys)} dispositivos...")

        for key in keys:
            last = heartbeat_timestamps.get(key)
            if last is None:
                continue

            diferencia = now - last
            print(f"[DEBUG] {key}: diferencia={diferencia:.2f}s")

            id_pond, id_device = key.split("/")
            sensores = pond_data.get(id_pond, {})

            tipo_dispositivo = None  # "sensor", "actuator" o None

            for sensor_id, sensor_data in sensores.items():
                if id_device == sensor_id:
                    tipo_dispositivo = "sensor"
                    break
                if id_device in sensor_data.get("actuators", {}):
                    tipo_dispositivo = "actuator"
                    break

            # Eliminar timestamp si el dispositivo ya no existe
            # if tipo_dispositivo is None:
            #     print(f"[AVISO] Dispositivo ya no está registrado en pond_data: {key}")
            #     with lock:
            #         heartbeat_timestamps.pop(key, None)
            #     continue

            if tipo_dispositivo is None:
                if diferencia > 5:
                    print(f"[ERROR HEARTBEAT] Dispositivo no encontrado tras timeout: {key}")
                    topic = f"aquanest/{id_pond}/{id_device}/heartbeat/error"
                    client.publish(topic, "error")
                    with lock:
                        heartbeat_timestamps.pop(key, None)
                else:
                    print(f"[AVISO] Dispositivo {key} no encontrado, esperando timeout...")
                continue

            # Publicar error si no hay heartbeat reciente
            # if diferencia > 5:
            #     topic = f"aquanest/{id_pond}/{id_device}/heartbeat/error"
            #     print(f"[ERROR HEARTBEAT] Publicado en {topic}")
            #     client.publish(topic, "error")
            if diferencia > 5:
                topic = f"aquanest/{id_pond}/{id_device}/heartbeat/error"
                print(f"[ERROR HEARTBEAT] Publicado en {topic}")
                client.publish(topic, "error")
                with lock:
                    heartbeat_timestamps.pop(key, None)
        time.sleep(1)