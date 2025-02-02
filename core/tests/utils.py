import os
import shutil


# utility function to communicate with the cat via websocket
def send_websocket_message(msg, client):

    with client.websocket_connect("/ws") as websocket:
        
        # sed ws message
        websocket.send_json(msg)

        # get reply
        reply = websocket.receive_json()
    
    return reply


# utility to send n messages via chat
def send_n_websocket_messages(num_messages, client):

    responses = []
    for m in range(num_messages):
        message = {
            "text": f"Red Queen {m}"
        }
        res = send_websocket_message(message, client)
        responses.append(res)

    return responses
            

def key_in_json(key, json):
    return key in json.keys()


def create_mock_plugin_zip():
    return shutil.make_archive(
        "tests/mocks/mock_plugin",
        "zip",
        root_dir="tests/mocks/",
        base_dir="mock_plugin"
    )


# utility to retrieve embedded tools from endpoint
def get_embedded_tools(client):
    params = {
        "text": "random"
    }
    response = client.get(f"/memory/recall/", params=params)
    json = response.json()
    return json["vectors"]["collections"]["procedural"]


# utility to retrieve declarative memory contents
def get_declarative_memory_contents(client):
    params = {
        "text": "Something"
    }
    response = client.get(f"/memory/recall/", params=params)
    assert response.status_code == 200
    json = response.json()
    declarative_memories = json["vectors"]["collections"]["declarative"]
    return declarative_memories


# utility to get collections and point count from `GET /memory/collections` in a simpler format
def get_collections_names_and_point_count(client):

    response = client.get("/memory/collections/")
    json = response.json()
    assert response.status_code == 200
    collections_n_points = { c["name"]: c["vectors_count"] for c in json["collections"]}
    return collections_n_points