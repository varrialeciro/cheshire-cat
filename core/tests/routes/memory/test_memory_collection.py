from tests.utils import send_websocket_message, get_collections_names_and_point_count


def test_memory_collections_created(client):

    # get collections
    response = client.get("/memory/collections/")
    json = response.json()
    assert response.status_code == 200
    
    # check default collections are created
    default_collections = ["episodic", "declarative", "procedural"]
    assert json["results"] == len(default_collections)
    assert len(json["collections"]) == len(default_collections)
    
    # check correct number of default points
    collections_n_points = { c["name"]: c["vectors_count"] for c in json["collections"]}
    # there is at least an embedded tool in procedural collection
    assert collections_n_points["procedural"] == 1
    # all other collections should be empty
    assert collections_n_points["episodic"] == 0
    assert collections_n_points["declarative"] == 0


def test_memory_collection_episodic_stores_messages(client):

    # before sending messages, episodic memory should be empty
    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["episodic"] == 0

    # send message via websocket
    message = {
        "text": "Meow"
    }
    res = send_websocket_message(message, client)
    assert type(res["content"]) == str

    # episodic memory should now contain one point
    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["episodic"] == 1

    # TOODO: check point metadata


def test_memory_collection_episodic_cleared(client):

    # send message via websocket
    message = {
        "text": "Meow"
    }
    res = send_websocket_message(message, client)
    assert type(res["content"]) == str

    # episodic memory should now contain one point
    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["episodic"] == 1

    # delete episodic memory
    response = client.delete("/memory/collections/episodic")
    json = response.json()
    assert response.status_code == 200
    
    # episodic memory should be empty
    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["episodic"] == 0


def test_memory_collection_procedural_has_tools_after_clear(client):

    # procedural emmory contains one tool (get_the_time)
    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["procedural"] == 1

    # delete procedural memory
    response = client.delete("/memory/collections/procedural")
    json = response.json()
    assert response.status_code == 200
    
    # tool should be automatically re-embedded after memory deletion
    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["procedural"] == 1 # still 1!


def test_memory_collections_wipe(client):

    #create episodic memory
    message = {
        "text": "Meow"
    }
    res = send_websocket_message(message, client)
    
    # create declarative memories
    file_name = "sample.txt"
    file_path = f"tests/mocks/{file_name}"
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_name, f, "text/plain")
        }
        response = client.post("/rabbithole/", files=files)

    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["procedural"] == 1   # default tool
    assert collections_n_points["episodic"] == 1      # websocket msg
    assert collections_n_points["declarative"] > 1  # several chunks

    # wipe out all memories
    response = client.delete("/memory/wipe-collections/")
    json = response.json()
    assert response.status_code == 200

    collections_n_points = get_collections_names_and_point_count(client)
    assert collections_n_points["procedural"] == 1   # default tool is re-emebedded
    assert collections_n_points["episodic"] == 0
    assert collections_n_points["declarative"] == 0