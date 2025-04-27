# store.py
from collections import defaultdict

# Estructura: id_pond -> id_sensor -> {"min": val, "max": val, "actuators": {...}}
pond_data = defaultdict(dict)

def set_sensor_threshold(id_pond, id_sensor, min_val, max_val, actuators):
    pond_data[id_pond][id_sensor] = {
        "min": min_val,
        "max": max_val,
        "actuators": actuators
    }

def get_sensor_info(id_pond, id_sensor):
    return pond_data.get(id_pond, {}).get(id_sensor)

def delete_pond(id_pond):
    pond_data.pop(id_pond, None)
