import json
import pandas as pd

with open("projet-info-2a/data/AtomicCards.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# La structure de AtomicCards.json contient probablement un dict avec des listes de cartes
# Exemple : { "data": { "Anax and Cymede": [ {...}, {...} ], "Another Card": [ {...}] } }

# On extrait toutes les cartes dans une seule liste
cards = []
for name, versions in data["data"].items():
    for card in versions:
        cards.append(card)

df = pd.DataFrame(cards)

print(df.keys())
