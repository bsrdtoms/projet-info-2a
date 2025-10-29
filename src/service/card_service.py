import pandas as pd
from technical_components.embedding.ollama_embedding import get_embedding
from technical_components.embedding.cosine_similarity import cosine_similarity
from dao.card_dao import CardDao
from business_object.card import Card
import random


class CardService:
    def __init__(self):
        self.dao = CardDao()

    def add_card(self, carte: Card):
        """
        Ajoute une carte en générant son embedding avant insertion
        """
        try:
            # Générer l'embedding
            embedding = get_embedding(carte.text)["embeddings"][0]
            carte.embedding_of_text = embedding

            # Persister via DAO
            return self.dao.create(carte)

        except Exception as e:
            print(f"Impossible d’ajouter la carte: {e}")
            return False

    def modify_card(self):
        """ 

        Parameters
        ----------------

        Returns
        ----------------
        
        """
        pass

    def delete_card(self):
        """ 

        Parameters
        ----------------

        Returns
        ----------------
        
        """
        pass

    def search_by_name(self, name):
        """
        Recherche les cartes dont le nom contient 'name'.

        Parameters
        ----------------
        name : str
            Nom (ou partie du nom) de la carte à rechercher.

        Returns
        ----------------
        cards : list[Card]
            Liste d'objets Card correspondant aux résultats de la recherche.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Le nom de la carte doit être une chaîne de caractère non vide.")

        cartes_trouvees = self.dao.search_by_name(name)

        if not cartes_trouvees:
            print(f"Aucune carte trouvée pour '{name}'.")
            return []

        return cartes_trouvees

    def get_all_embeddings(self):
        """
        Utilise le DAO pour récupérer toutes les cartes
        et les transforme en DataFrame exploitable.
        """
        cards = self.dao.list_all()

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

    def semantic_search(self, text: str, top_k: int = 5) -> str:
        """
        Trouve les cartes les plus similaires à un texte donné.

        Args:
            text (str): Le texte à matcher
            top_k (int): Nombre de cartes similaires à retourner

        Returns:
            str: Le nom de la carte la plus proche
        """
        r = get_embedding(text)["embeddings"][0]
        df_with_embeddings = self.get_all_embeddings()

        similarities = []
        for _, row in df_with_embeddings.iterrows():
            embedding = row['embedding_of_text']
            similarity = cosine_similarity(r, embedding)
            similarities.append(similarity)

        df_with_embeddings['similarity'] = similarities

        results = df_with_embeddings.nlargest(top_k, 'similarity')

        return results.iloc[0]["name"]

    def random(self):
        """ 

        Parameters
        ----------------

        Returns
        ----------------
        
        """
        cartes = self.dao.list_all()
        if not cartes:
            return None
        return random.choice(cartes)
