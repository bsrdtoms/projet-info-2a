import pandas as pd
from technical_components.embedding.ollama_embedding import get_embedding
from technical_components.embedding.cosine_similarity import cosine_similarity
from dao.card_dao import CardDao
from business_object.card import Card
import random


class CardService:
    """Service pour gérer les opérations sur les cartes"""

    def __init__(self):
        self.dao = CardDao()

    def add_card(self, carte: Card) -> bool:
        """
        Ajoute une carte en générant son embedding avant insertion

        Parameters
        ----------
        carte : Card
            Carte à ajouter

        Returns
        -------
        bool
            True si succès, False sinon
        """
        try:
            # Générer l'embedding si un texte existe
            if carte.text:
                embedding_response = get_embedding(carte.text)
                carte.embedding_of_text = embedding_response["embeddings"][0]

            # Persister via DAO
            print(f"Création de la carte : {carte.name}")
            return self.dao.create(carte)

        except Exception as e:
            print(f"Impossible d’ajouter la carte: {e}")
            return False

    def modify_card(self, card_id: int, field: str, value) -> bool:
        """
        Modifier un champ d'une carte

        Parameters
        ----------------
        card_id : int
            Identifiant de la carte à modifier
        updates : dict
            Dictionnaire {colonne: nouvelle_valeur} à mettre à jour

        Returns
        -------
        bool
        """
        return self.dao.modify(card_id, field, value)
        
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

    def semantic_search(self, text: str, top_k: int = 5):
        """
        Recherche sémantique OPTIMISÉE avec pgvector

        AVANT: Récupérait toutes les cartes, calculait en Python (lent)
        APRÈS: Tout le calcul se fait en SQL (rapide)

        Parameters
        ----------
        text : str
            Texte de recherche
        top_k : int
            Nombre de résultats à retourner

        Returns
        -------
        list[dict]
            Liste de résultats avec id, name, text, similarity
        """
        try:
            # 1. Générer l'embedding du texte de recherche
            embedding_response = get_embedding(text)
            query_embedding = embedding_response["embeddings"][0]

            # 2. Recherche directe en SQL via pgvector (RAPIDE!)
            # Plus besoin de boucle Python ni de pandas!
            results = self.dao.semantic_search(query_embedding, top_k)

            return results

        except Exception as e:
            print(f"❌ Erreur lors de la recherche sémantique: {e}")
            raise

    def random(self):
        """
        Récupérer une carte aléatoire

        Returns
        -------
        Card ou None
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
