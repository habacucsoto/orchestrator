from mqtt_client import client
import logging
from orchestrator.store import get_sensor_info

# Diccionario para hacer seguimiento de respuestas pendientes
pending_actions = {}

# CODIGO ANTERIOR 
# def trigger_action(id_pond, id_sensor, value, actuators):
#     alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous/value"
#     client.publish(alert_topic, str(value))
#     logging.info(f"Valor anómalo detectado: {value} en {id_sensor} (estanque {id_pond})")

#     for act_type, act_id in actuators.items():
#         action_topic = f"aquanest/{id_pond}/{act_id}/action/on"
#         client.publish(action_topic, "on")
#         pending_actions[(id_pond, act_id)] = "on"
#         logging.info(f"Acción enviada: {act_type} ({act_id}) → ON")

def trigger_action(id_pond, id_sensor, value, actuators):
    sensor_info = get_sensor_info(id_pond, id_sensor)
    if not sensor_info:
        logging.warning(f"No se encontró información del sensor {id_sensor} en el estanque {id_pond}")
        return

    min_val = sensor_info["min"]
    max_val = sensor_info["max"]
    sensor_type = "temperatura" if "CAL" in actuators or "ENF" in actuators else "nh4no3"

    # Revisar valor anómalo
    is_anomalous = False
    if sensor_type == "temperatura":
        if value < min_val:
            act_type = "CAL"
            is_anomalous = True
        elif value > max_val:
            act_type = "ENF"
            is_anomalous = True
        else:
            logging.info(f"Valor de temperatura {value} dentro de umbrales para {id_sensor}")
            return
    elif sensor_type == "nh4no3":
        if value > max_val:
            act_type = "BR"
            is_anomalous = True
        else:
            logging.info(f"Valor de NH4NO3 {value} dentro de umbrales para {id_sensor}")
            return

    # Publicar alerta y activar actuador si fue anómalo
    if is_anomalous:
        alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous/value"
        client.publish(alert_topic, str(value))
        logging.info(f"Valor anómalo detectado: {value} en {id_sensor} (estanque {id_pond})")

        actuator_id = actuators.get(act_type)
        if actuator_id:
            action_topic = f"aquanest/{id_pond}/{actuator_id}/action/on"
            client.publish(action_topic, "on")
            pending_actions[(id_pond, actuator_id)] = "on"
            logging.info(f"Acción enviada: {act_type} ({actuator_id}) → ON")
        else:
            logging.warning(f"No se encontró actuador para tipo {act_type} en {id_sensor}")


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
