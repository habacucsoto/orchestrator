from mqtt_client import client
from store import get_sensor_info

pending_actions = {}
actuator_states = {} 

def trigger_action(id_pond, id_sensor, value, actuators):
    sensor_info = get_sensor_info(id_pond, id_sensor)
    if not sensor_info:
        print(f"No se encontró información del sensor {id_sensor} en el estanque {id_pond}")
        return

    min_val = sensor_info["min"]
    max_val = sensor_info["max"]
    sensor_type = "temperatura" if "CAL" in actuators or "ENF" in actuators else "nh4no3"

    desired_actuator_on = None 
    actuators_to_turn_off = [] 
    is_anomalous = False 

    if sensor_type == "temperatura":
        cal_actuator = actuators.get("CAL")
        enf_actuator = actuators.get("ENF")

        if value < min_val:
            desired_actuator_on = cal_actuator
            if enf_actuator:
                actuators_to_turn_off.append(enf_actuator)
            is_anomalous = True
        elif value > max_val:
            desired_actuator_on = enf_actuator
            if cal_actuator:
                actuators_to_turn_off.append(cal_actuator)
            is_anomalous = True
        else:
            print(f"Valor de temperatura {value} dentro de umbrales para {id_sensor}")
            if cal_actuator:
                actuators_to_turn_off.append(cal_actuator)
            if enf_actuator:
                actuators_to_turn_off.append(enf_actuator)

    elif sensor_type == "nh4no3":
        br_actuator = actuators.get("BR")
        if value > max_val:
            desired_actuator_on = br_actuator
            is_anomalous = True 
        if value < min_val and br_actuator:
            actuators_to_turn_off.append(br_actuator)
            is_anomalous = True
        else:
            print(f"Valor de NH4NO3 {value} dentro de umbrales para {id_sensor}")
            if br_actuator:
                actuators_to_turn_off.append(br_actuator)

    if is_anomalous:
        alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous"
        client.publish(alert_topic, str(value))
        print(f"Valor anómalo detectado: {value} en {id_sensor} (estanque {id_pond})")

    if desired_actuator_on:
        actuator_key_on = (id_pond, desired_actuator_on)
        if actuator_states.get(actuator_key_on) != "on":
            action_topic_on = f"aquanest/{id_pond}/{desired_actuator_on}/action"
            client.publish(action_topic_on, "on")
            pending_actions[actuator_key_on] = "on"
            actuator_states[actuator_key_on] = "on"
            print(f"Acción enviada: {desired_actuator_on} → ON")
        else:
            print(f"El actuador {desired_actuator_on} en {id_pond} ya está ON, no se reenvía acción.")

    for actuator_id_off in actuators_to_turn_off:
        if actuator_id_off == desired_actuator_on:
            continue 
        actuator_key_off = (id_pond, actuator_id_off)
        if actuator_states.get(actuator_key_off) != "off":
            action_topic_off = f"aquanest/{id_pond}/{actuator_id_off}/action"
            client.publish(action_topic_off, "off")
            pending_actions[actuator_key_off] = "off"
            actuator_states[actuator_key_off] = "off"
            print(f"Acción enviada: {actuator_id_off} → OFF")
        else:
            print(f"ℹEl actuador {actuator_id_off} en {id_pond} ya está OFF.")


def handle_response_message(topic, payload):
    parts = topic.split("/")
    id_pond = parts[1]
    id_actuator = parts[2]
    key = (id_pond, id_actuator)
    desired_state = pending_actions.get(key)

    if not desired_state:
        return

    status_topic = f"aquanest/{id_pond}/{id_actuator}/status"
    received_status = payload.decode()

    if received_status == "ok":
        client.publish(status_topic, desired_state)
        print(f"Confirmación de estado: {id_actuator} en {id_pond} → {desired_state}")
    else:
        client.publish(status_topic, "error")
        actuator_states[key] = "error" 

    if key in pending_actions:
        del pending_actions[key]