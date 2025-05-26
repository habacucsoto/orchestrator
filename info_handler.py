# import json
# from store import set_sensor_threshold

# def handle_info_message(topic, payload):
#     data = json.loads(payload)
#     print(data)
#     for id_pond, sensors in data.items():
#         for sensor_id, config in sensors.items():
#             if "temperatura_maxima" in config:
#                 set_sensor_threshold(
#                     id_pond, sensor_id,
#                     config["temperatura_minima"],
#                     config["temperatura_maxima"],
#                     {
#                         "CAL": config["CAL_id"],
#                         "ENF": config["ENF_id"]
#                     }
#                 )
#             elif "nh4no3_maximo" in config:
#                 set_sensor_threshold(
#                     id_pond, sensor_id,
#                     config["nh4no3_minimo"],
#                     config["nh4no3_maximo"],
#                     {
#                         "BR": config["BR_id"]
#                     }
#                 )

# import json
# from store import set_sensor_threshold

# def handle_info_message(topic, payload):
#     data = json.loads(payload)
#     print("Información recibida para configurar estanques:", data)

#     # El id_pond se extrae directamente como la clave principal del JSON
#     # Por ejemplo, "E68"
#     for id_pond, sensors_data in data.items():
#         for sensor_id, config in sensors_data.items():
#             # Los ids de sensor (ej. "ST135", "SN136") también se extraen directamente

#             if "temperatura_maxima" in config:
#                 # Para sensores de temperatura, usamos 'id_calentador' y 'id_refrigerador'
#                 set_sensor_threshold(
#                     id_pond, sensor_id,
#                     config["temperatura_minima"],
#                     config["temperatura_maxima"],
#                     {
#                         "CAL": config["id_calentador"], # Ahora se usa 'id_calentador'
#                         "ENF": config["id_refrigerador"] # Ahora se usa 'id_refrigerador'
#                     }
#                 )
#                 print(f"Configurado sensor de temperatura {sensor_id} en estanque {id_pond}: Min={config['temperatura_minima']}, Max={config['temperatura_maxima']}, Calentador={config['id_calentador']}, Enfriador={config['id_refrigerador']}")
#             elif "nh4no3_maximo" in config:
#                 # Para sensores de NH4NO3, usamos 'id_bomba'
#                 set_sensor_threshold(
#                     id_pond, sensor_id,
#                     config["nh4no3_minimo"],
#                     config["nh4no3_maximo"],
#                     {
#                         "BR": config["id_bomba"] # Ahora se usa 'id_bomba'
#                     }
#                 )
#                 print(f"Configurado sensor de NH4NO3 {sensor_id} en estanque {id_pond}: Min={config['nh4no3_minimo']}, Max={config['nh4no3_maximo']}, Bomba={config['id_bomba']}")


import json
from store import set_sensor_threshold

def handle_info_message(topic, payload):
    data = json.loads(payload)
    print("Información recibida para configurar estanques:", data)

    for id_pond, sensors_data in data.items():
        for sensor_id, config in sensors_data.items():
            if "temperatura_maxima" in config:
                # --- Lógica para el calentador ---
                cal_act_id_raw = None
                if "id_calentador" in config:
                    cal_act_id_raw = config["id_calentador"]
                elif "CAL_id" in config: # Soporte para el formato antiguo
                    cal_act_id_raw = config["CAL_id"]

                cal_act_id = None
                if cal_act_id_raw is not None:
                    # Si el ID es un número, lo convertimos a string con el prefijo
                    if isinstance(cal_act_id_raw, int):
                        cal_act_id = f"CAL{cal_act_id_raw}"
                    else: # Si ya es un string (ej. "CAL202"), lo usamos tal cual
                        cal_act_id = cal_act_id_raw

                # --- Lógica para el refrigerador ---
                enf_act_id_raw = None
                if "id_refrigerador" in config:
                    enf_act_id_raw = config["id_refrigerador"]
                elif "ENF_id" in config: # Soporte para el formato antiguo
                    enf_act_id_raw = config["ENF_id"]

                enf_act_id = None
                if enf_act_id_raw is not None:
                    if isinstance(enf_act_id_raw, int):
                        enf_act_id = f"ENF{enf_act_id_raw}"
                    else:
                        enf_act_id = enf_act_id_raw

                # Asegurarse de que al menos se haya encontrado uno para continuar
                if cal_act_id is None and enf_act_id is None:
                    print(f"Advertencia: No se encontraron IDs válidos para calentador o enfriador en el sensor {sensor_id} del estanque {id_pond}")
                    continue

                set_sensor_threshold(
                    id_pond, sensor_id,
                    config["temperatura_minima"],
                    config["temperatura_maxima"],
                    {
                        "CAL": cal_act_id,
                        "ENF": enf_act_id
                    }
                )
                print(f"Configurado sensor de temperatura {sensor_id} en estanque {id_pond}: Min={config['temperatura_minima']}, Max={config['temperatura_maxima']}, Calentador={cal_act_id}, Enfriador={enf_act_id}")

            elif "nh4no3_maximo" in config:
                # --- Lógica para la bomba ---
                br_act_id_raw = None
                if "id_bomba" in config:
                    br_act_id_raw = config["id_bomba"]
                elif "BR_id" in config: # Soporte para el formato antiguo
                    br_act_id_raw = config["BR_id"]

                br_act_id = None
                if br_act_id_raw is not None:
                    if isinstance(br_act_id_raw, int):
                        br_act_id = f"BR{br_act_id_raw}"
                    else:
                        br_act_id = br_act_id_raw

                if br_act_id is None:
                    print(f"Advertencia: No se encontró ID válido para la bomba en el sensor {sensor_id} del estanque {id_pond}")
                    continue

                set_sensor_threshold(
                    id_pond, sensor_id,
                    config["nh4no3_minimo"],
                    config["nh4no3_maximo"],
                    {
                        "BR": br_act_id
                    }
                )
                print(f"Configurado sensor de NH4NO3 {sensor_id} en estanque {id_pond}: Min={config['nh4no3_minimo']}, Max={config['nh4no3_maximo']}, Bomba={br_act_id}")