import time
import json
import paho.mqtt.publish as publish

BROKER = "192.168.100.7"  
ID_POND = "pond001"
TEMP_SENSOR = "sensor_temp_1"
NH4NO3_SENSOR = "sensor_nh4no3_1"
REFRIGERATOR_ID = "refrig001"
HEATER_ID = "heater001"
PUMP_ID = "pump001"

# 1. Publicar configuración inicial
def test_info():
    payload = {
        ID_POND: {
            TEMP_SENSOR: {
                "temperatura_maxima": 25.0,
                "temperatura_minima": 20.0,
                "id_refrigerador": REFRIGERATOR_ID,
                "id_calentador": HEATER_ID
            },
            NH4NO3_SENSOR: {
                "nh4no3_maximo": 15.0,
                "nh4no3_minimo": 5.0,
                "id_bomba": PUMP_ID
            }
        }
    }
    publish.single(f"aquanest/{ID_POND}/{TEMP_SENSOR}/info", json.dumps(payload), hostname=BROKER)
    print("Configuración de sensores enviada")
    time.sleep(1)

# 2. Enviar valores dentro del umbral (deberían ser ignorados)
def test_normal_data():
    publish.single(f"aquanest/{ID_POND}/{TEMP_SENSOR}/data/value", "22.5", hostname=BROKER)
    publish.single(f"aquanest/{ID_POND}/{NH4NO3_SENSOR}/data/value", "10.0", hostname=BROKER)
    print("Datos normales enviados")
    time.sleep(1)

# 3. Enviar valores fuera del umbral
def test_anomalous_data():
    publish.single(f"aquanest/{ID_POND}/{TEMP_SENSOR}/data/value", "28.0", hostname=BROKER)  # Alta temperatura
    publish.single(f"aquanest/{ID_POND}/{NH4NO3_SENSOR}/data/value", "3.0", hostname=BROKER)  # NH4NO3 bajo
    print("Datos fuera de umbral enviados")
    time.sleep(1)

# 4. Simular heartbeats
def test_heartbeats():
    for _ in range(3):
        publish.single(f"aquanest/{ID_POND}/{TEMP_SENSOR}/heartbeat", "ok", hostname=BROKER)
        publish.single(f"aquanest/{ID_POND}/{REFRIGERATOR_ID}/heartbeat", "ok", hostname=BROKER)
        time.sleep(1)
    print("Heartbeats simulados")

# 5. Simular pérdida de heartbeat
def test_missing_heartbeat():
    print("Simulando pérdida de heartbeat...")
    time.sleep(3)  # Dejar que el orquestador detecte la ausencia

# 6. Eliminar estanque
def test_delete_pond():
    publish.single(f"aquanest/{ID_POND}/delete", "", hostname=BROKER)
    print("Estanque eliminado")
    time.sleep(1)

if __name__ == "__main__":
    test_info()
    test_normal_data()
    test_anomalous_data()
    test_heartbeats()
    test_missing_heartbeat()
    test_delete_pond()
