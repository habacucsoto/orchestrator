from store import get_sensor_info
from actuator_handler import trigger_action
import json

def handle_data_message(topic, payload):
    parts = topic.split("/")
    id_pond, id_sensor = parts[1], parts[2]
    value = float(payload)

    sensor_info = get_sensor_info(id_pond, id_sensor)
    if sensor_info is None:
        return

    if not (sensor_info["min"] <= value <= sensor_info["max"]):
        trigger_action(id_pond, id_sensor, value, sensor_info["actuators"])