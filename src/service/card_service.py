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
            print(f"Création de la carte : {carte.name}")
            return self.dao.create(carte)

        except Exception as e:
            print(f"Impossible d’ajouter la carte: {e}")
            return False

    def modify_card(self):
        """ 

        Parameters
        ----------------
        card_id : int
            Identifiant de la carte à modifier
        updates : dict
            Dictionnaire {colonne: nouvelle_valeur} à mettre à jour

        Returns
        ----------------
        
        """
        pass

    def delete_card(self, carte: Card):
        """
        Supprime une carte en base de données

        Parameters
        ----------------
        carte : Card
            Objet représentant la carte à supprimer

        Returns
        ----------------
        deleted : bool
            True si la suppression a réussi
            False sinon
        """
        print(f"Tentative de suppression de la carte : {carte.name} (id={carte.id})")
        return self.dao.delete(carte)

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
        print(max(df_with_embeddings['similarity']))
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

    def random_by_id(self):
        """méthode random plus rapide"""
        ids = self.dao.get_all_ids()
        if not ids:
            return None
        random_id = random.choice(ids)
        return self.dao.search_by_id(random_id)
