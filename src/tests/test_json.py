import json

with open("data/AtomicCards.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(type(data))
if isinstance(data, dict):
    print("Clés disponibles :", list(data.keys())[:10])
elif isinstance(data, list):
    print("Nombre d’éléments :", len(data))
    print("Premier élément :", data[0])
