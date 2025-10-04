""" C'EST QUOI CE FICHIER ???????? """


import os
import requests


def get_embedding(text):
    token = os.getenv("API_TOKEN")
    url = "https://llm.lab.sspcloud.fr/ollama/api/embed"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "bge-m3:latest",
        "input": text
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()
