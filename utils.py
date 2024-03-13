import requests

def fetch_ollama_models(ollama_url):
    models_data = requests.get("{}/api/tags".format(ollama_url))
    models = [x["model"] for x in models_data.json()["models"]]
    return models
