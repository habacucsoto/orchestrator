from mqtt_client import client, start_mqtt
from info_handler import handle_info_message
from data_handler import handle_data_message
from delete_handler import handle_delete_message
from heartbeat_monitor import update_heartbeat, monitor_heartbeats
from actuator_handler import handle_response_message
import threading

TOPICS = [
    ("aquanest/+/info", 0),
    ("aquanest/+/+/data/+", 0),
    ("aquanest/+/delete", 0),
    ("aquanest/+/+/heartbeat", 0),
    ("aquanest/+/+/response", 0)
]

def on_message(client, userdata, msg):
    if "/info" in msg.topic:
        handle_info_message(msg.topic, msg.payload)
    elif "/data/" in msg.topic:
        handle_data_message(msg.topic, msg.payload)
    elif "/delete" in msg.topic:
        handle_delete_message(msg.topic, msg.payload)
    elif "/heartbeat" in msg.topic:
        parts = msg.topic.split("/")
        update_heartbeat(parts[1], parts[2])
    elif "/response" in msg.topic:
        print('suscrito response')
        handle_response_message(msg.topic, msg.payload)

if __name__ == "__main__":
    start_mqtt(on_message)
    for topic in TOPICS:
        client.subscribe(topic)
    threading.Thread(target=monitor_heartbeats, daemon=True).start()

    input("Presiona Enter para salir...\n")
