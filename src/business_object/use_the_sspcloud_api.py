import os
import requests


token = os.getenv("API_TOKEN")
print(token)
url = "https://llm.lab.sspcloud.fr/ollama/api/embed"

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

data = {
    "model": "bge-m3:latest",
    "input": "Is the sky blue"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
