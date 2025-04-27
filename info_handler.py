import json
from store import set_sensor_threshold

def handle_info_message(topic, payload):
    data = json.loads(payload)
    for id_pond, sensors in data.items():
        for sensor_id, config in sensors.items():
            if "temperatura_maxima" in config:
                set_sensor_threshold(
                    id_pond, sensor_id,
                    config["temperatura_minima"],
                    config["temperatura_maxima"],
                    {"refrigerador": config["id_refrigerador"], "calentador": config["id_calentador"]}
                )
            elif "nh4no3_maximo" in config:
                set_sensor_threshold(
                    id_pond, sensor_id,
                    config["nh4no3_minimo"],
                    config["nh4no3_maximo"],
                    {"bomba": config["id_bomba"]}
                )
