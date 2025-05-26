from mqtt_client import client
from store import get_sensor_info

# Diccionario para hacer seguimiento de respuestas pendientes
pending_actions = {}
actuator_states = {} # This will store the current known state of an actuator ('on' or 'off')

def trigger_action(id_pond, id_sensor, value, actuators):
    sensor_info = get_sensor_info(id_pond, id_sensor)
    if not sensor_info:
        print(f"No se encontró información del sensor {id_sensor} en el estanque {id_pond}")
        return

    min_val = sensor_info["min"]
    max_val = sensor_info["max"]
    sensor_type = "temperatura" if "CAL" in actuators or "ENF" in actuators else "nh4no3"

    # # Determine the desired state for all related actuators
    # desired_actuator_on = None # The actuator that should be ON
    # actuators_to_turn_off = [] # List of actuators that should be OFF
    # is_anomalous = False # Initialize is_anomalous to False

    # if sensor_type == "temperatura":
    #     cal_actuator = actuators.get("CAL")
    #     enf_actuator = actuators.get("ENF")

    #     if value < min_val:
    #         desired_actuator_on = cal_actuator
    #         if enf_actuator:
    #             actuators_to_turn_off.append(enf_actuator)
    #     elif value > max_val:
    #         desired_actuator_on = enf_actuator
    #         if cal_actuator:
    #             actuators_to_turn_off.append(cal_actuator)
    #     else:
    #         print(f"Valor de temperatura {value} dentro de umbrales para {id_sensor}")
    #         # If within range, ensure both are off
    #         if cal_actuator:
    #             actuators_to_turn_off.append(cal_actuator)
    #         if enf_actuator:
    #             actuators_to_turn_off.append(enf_actuator)

    # elif sensor_type == "nh4no3":
    #     br_actuator = actuators.get("BR")
    #     if value > max_val:
    #         desired_actuator_on = br_actuator
    #     else:
    #         print(f"Valor de NH4NO3 {value} dentro de umbrales para {id_sensor}")
    #         # If within range, ensure it's off
    #         if br_actuator:
    #             actuators_to_turn_off.append(br_actuator)

    # # If no actuator needs to be turned on (e.g., within range), just turn off others
    # if not desired_actuator_on and not actuators_to_turn_off:
    #     return # No action needed

    # # Publish alert if anomalous
    # is_anomalous = (desired_actuator_on is not None)
    # if is_anomalous:
    #     alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous"
    #     client.publish(alert_topic, str(value))
    #     print(f"Valor anómalo detectado: {value} en {id_sensor} (estanque {id_pond})")

    # Determine the desired state for all related actuators
    desired_actuator_on = None # The actuator that should be ON
    actuators_to_turn_off = [] # List of actuators that should be OFF
    is_anomalous = False # Initialize is_anomalous to False

    if sensor_type == "temperatura":
        cal_actuator = actuators.get("CAL")
        enf_actuator = actuators.get("ENF")

        if value < min_val:
            desired_actuator_on = cal_actuator
            if enf_actuator:
                actuators_to_turn_off.append(enf_actuator)
            is_anomalous = True # It's anomalous if below min
        elif value > max_val:
            desired_actuator_on = enf_actuator
            if cal_actuator:
                actuators_to_turn_off.append(cal_actuator)
            is_anomalous = True # It's anomalous if above max
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
            is_anomalous = True # It's anomalous if above max
        else:
            print(f"Valor de NH4NO3 {value} dentro de umbrales para {id_sensor}")
            if br_actuator:
                actuators_to_turn_off.append(br_actuator)

    # Publish alert if anomalous
    if is_anomalous:
        alert_topic = f"aquanest/{id_pond}/{id_sensor}/alert/anomalous"
        client.publish(alert_topic, str(value))
        print(f"Valor anómalo detectado: {value} en {id_sensor} (estanque {id_pond})")

    # Handle turning ON the desired actuator
    if desired_actuator_on:
        actuator_key_on = (id_pond, desired_actuator_on)
        # Check current state; if it's not 'on', send the command
        if actuator_states.get(actuator_key_on) != "on":
            action_topic_on = f"aquanest/{id_pond}/{desired_actuator_on}/action"
            client.publish(action_topic_on, "on")
            pending_actions[actuator_key_on] = "on"
            # Immediately update the internal state to 'on' *after* sending the command
            # This optimistically assumes the command will be successful, reducing redundant messages.
            # The 'handle_response_message' will correct it if it fails.
            actuator_states[actuator_key_on] = "on"
            print("VALOR POND", id_pond)
            print("Desired actuator", desired_actuator_on)
            print(f"Acción enviada: {desired_actuator_on} → ON")
        else:
            print(f"⚠️ El actuador {desired_actuator_on} en {id_pond} ya está ON, no se reenvía acción.")

    # Handle turning OFF other actuators
    for actuator_id_off in actuators_to_turn_off:
        if actuator_id_off == desired_actuator_on:
            continue # Don't try to turn off the one we want to turn on
        actuator_key_off = (id_pond, actuator_id_off)
        # Check current state; if it's not 'off', send the command
        if actuator_states.get(actuator_key_off) != "off":
            action_topic_off = f"aquanest/{id_pond}/{actuator_id_off}/action"
            client.publish(action_topic_off, "off")
            pending_actions[actuator_key_off] = "off"
            # Immediately update the internal state to 'off' after sending the command
            actuator_states[actuator_key_off] = "off"
            print(f"Acción enviada: {actuator_id_off} → OFF")
        else:
            print(f"ℹ️ El actuador {actuator_id_off} en {id_pond} ya está OFF.")


def handle_response_message(topic, payload):
    parts = topic.split("/")
    id_pond = parts[1]
    id_actuator = parts[2]
    key = (id_pond, id_actuator)
    desired_state = pending_actions.get(key)

    if not desired_state:
        print(f"Respuesta inesperada para {id_actuator} en estanque {id_pond} (no había acción pendiente).")
        return

    status_topic = f"aquanest/{id_pond}/{id_actuator}/status"
    received_status = payload.decode()

    if received_status == "ok":
        client.publish(status_topic, desired_state)
        print(f"✅ Confirmación de estado: {id_actuator} en {id_pond} → {desired_state}")
    else:
        client.publish(status_topic, "error")
        actuator_states[key] = "error" # Or some other indicator of failure
        print(f"❌ Error al activar/desactivar {id_actuator} en {id_pond}. Recibido: {received_status}")

    # Remove from pending actions regardless of success or failure
    if key in pending_actions:
        del pending_actions[key]