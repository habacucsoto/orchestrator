import time
import random  # Simulación de respuesta
import paho.mqtt.publish as publish

def trigger_action(id_pond, id_sensor, value, actuators):
    alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous/value"
    publish.single(alert_topic, str(value), hostname="localhost")

    for act_type, act_id in actuators.items():
        action_topic = f"aquanest/{id_pond}/{act_id}/action/on"
        publish.single(action_topic, "on", hostname="localhost")

        # Simulación de respuesta
        time.sleep(1)
        success = random.choice([True, False])
        response_topic = f"aquanest/{id_pond}/{act_id}/status/on" if success else f"aquanest/{id_pond}/{act_id}/status/error"
        publish.single(response_topic, "on" if success else "error", hostname="localhost")

