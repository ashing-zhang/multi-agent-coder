model_client = None

def set_model_client(client):
    global model_client
    model_client = client

def get_model_client():
    return model_client 