"""
Service pour les cartes Magic avec support pgvector optimisé
Remplace src/service/card_service.py

CHANGEMENTS PRINCIPAUX:
- Plus de boucle Python pour calculer les similarités
- Tout se passe en SQL avec pgvector
- Plus besoin de pandas ni de cosine_similarity manuel
"""

from technical_components.embedding.ollama_embedding import get_embedding
from dao.card_dao import CardDao
from business_object.card import Card


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
            return self.dao.create(carte)

        except Exception as e:
            print(f"❌ Impossible d'ajouter la carte: {e}")
            return False

    def modify_card(self, card_id: int, field: str, value) -> bool:
        """
        Modifier un champ d'une carte

        Parameters
        ----------
        card_id : int
            ID de la carte
        field : str
            Nom du champ à modifier
        value : any
            Nouvelle valeur

        Returns
        -------
        bool
        """
        return self.dao.modify(card_id, field, value)

    def delete_card(self, carte: Card) -> bool:
        """
        Supprimer une carte

        Parameters
        ----------
        carte : Card
            Carte à supprimer

        Returns
        -------
        bool
        """
        return self.dao.delete(carte)

    def search_by_name(self, name: str, limit: int = 10):
        """
        Rechercher des cartes par nom

        Parameters
        ----------
        name : str
            Nom ou partie du nom
        limit : int
            Nombre max de résultats

        Returns
        -------
        list[Card]
        """
        return self.dao.search_by_name(name, limit)

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

    def semantic_search_simple(self, text: str, top_k: int = 1) -> str:
        """
        Version simplifiée qui retourne juste le nom de la meilleure carte
        Compatible avec l'ancien code pour match_new_text

        Parameters
        ----------
        text : str
            Texte de recherche
        top_k : int
            Nombre de résultats (par défaut 1)

        Returns
        -------
        str
            Nom de la carte la plus similaire
        """
        results = self.semantic_search(text, top_k)
        if results:
            return results[0]["name"]
        return None

    def random(self):
        """
        Récupérer une carte aléatoire

        Returns
        -------
        Card ou None
        """
        return self.dao.random()

    def get_card_by_id(self, card_id: int):
        """
        Récupérer une carte par son ID

        Parameters
        ----------
        card_id : int

        Returns
        -------
        Card ou None
        """
        return self.dao.find_by_id(card_id)

    def list_all_cards(self):
        """
        Lister toutes les cartes

        Returns
        -------
        list[Card]
        """
        return self.dao.list_all()


