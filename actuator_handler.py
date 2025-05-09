from mqtt_client import client
import logging

# Diccionario para hacer seguimiento de respuestas pendientes
pending_actions = {}

def trigger_action(id_pond, id_sensor, value, actuators):
    alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous/value"
    client.publish(alert_topic, str(value))
    logging.info(f"Valor anómalo detectado: {value} en {id_sensor} (estanque {id_pond})")

    for act_type, act_id in actuators.items():
        action_topic = f"aquanest/{id_pond}/{act_id}/action/on"
        client.publish(action_topic, "on")
        pending_actions[(id_pond, act_id)] = "on"
        logging.info(f"Acción enviada: {act_type} ({act_id}) → ON")


def handle_response_message(topic, payload):
    parts = topic.split("/")
    id_pond = parts[1]
    id_actuator = parts[2]
    key = (id_pond, id_actuator)
    desired_state = pending_actions.get(key)

    if not desired_state:
        logging.warning(f"Respuesta inesperada para {id_actuator} en estanque {id_pond}")
        return

    status_topic = f"aquanest/{id_pond}/{id_actuator}/status"

    if payload.decode() == "ok":
        client.publish(status_topic, desired_state)
        logging.info(f"✅ Estado actualizado: {id_actuator} en {id_pond} → {desired_state}")
    else:
        client.publish(status_topic, "error")
        logging.warning(f"Error al activar {id_actuator} en {id_pond}")

    del pending_actions[key]
