import paho.mqtt.client as mqtt

client = mqtt.Client()

def start_mqtt(on_message_callback):
    client.on_connect = lambda c, u, f, rc: print("Conectado al broker")
    client.on_message = on_message_callback
    client.connect("192.168.100.7", 1883)
    client.loop_start()
