import pandas as pd
from dao.card_dao import CardDAO

class CardService:
    def __init__(self):
        pass

    def get_all_embeddings(self):
        """
        Utilise le DAO pour récupérer toutes les cartes
        et les transforme en DataFrame exploitable.
        """
        cards = CardDAO().list_all()

        if not cards:
            print("⚠️ No cards found in database.")
            return pd.DataFrame(columns=["id", "name", "embedding_of_text"])       # pourquoi on retourne ça du coup ?

        # Transformation des objets Card en dictionnaires
        data = [
            {"id": card.id, "name": card.name, "embedding_of_text": card.embedding_of_text}
            for card in cards
        ]

        df = pd.DataFrame(data, columns=["id", "name", "embedding_of_text"])
        return df
