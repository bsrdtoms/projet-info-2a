import json
import pandas as pd


def get_initial_data():
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
    # print(df.keys())

    return df


def get_data_with_embeddings():
    df = pd.read_json("projet-info-2a/data/cards_with_embeddings.json", lines=True)
    return df
