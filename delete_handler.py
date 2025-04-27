from store import delete_pond

def handle_delete_message(topic, payload):
    id_pond = topic.split("/")[1]
    delete_pond(id_pond)
