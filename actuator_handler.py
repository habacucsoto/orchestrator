import logging
from mqtt_client import client

# Cola de acciones pendientes
pending_actions = {}

def trigger_action(id_pond, id_sensor, value, actuators):
    alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous/value"
    client.publish(alert_topic, str(value))
    logging.info(f"Alerta publicada: {alert_topic} -> {value}")

    for act_type, act_id in actuators.items():
        action_topic = f"aquanest/{id_pond}/{act_id}/action/on"
        client.publish(action_topic, "on")
        logging.info(f"Acción publicada: {action_topic} -> on")

        pending_actions[(id_pond, act_id)] = "on"

def handle_response_message(topic, payload):
    parts = topic.split("/")
    if len(parts) != 4 or parts[3] != "response":
        return

    id_pond = parts[1]
    id_actuator = parts[2]
    key = (id_pond, id_actuator)
    payload = payload.decode().strip().lower()

    if key not in pending_actions:
        logging.warning(f"Respuesta inesperada de actuador {key}")
        return

    desired_state = pending_actions.pop(key)

    status_topic = f"aquanest/{id_pond}/{id_actuator}/status"
    if payload == "ok":
        client.publish(status_topic, desired_state)
        logging.info(f"Estado actualizado: {status_topic} -> {desired_state}")
    else:
        client.publish(status_topic, "error")
        logging.warning(f"Error del actuador {id_actuator}, publicado en status")
