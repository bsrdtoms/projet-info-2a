from technical_components.embedding.ollama_embedding import get_embedding
from dao.card_dao import CardDao
from business_object.card import Card
import random
from utils.log_decorator import log

class CardService:
    """Service pour gérer les opérations sur les cartes"""

    def __init__(self):
        self.dao = CardDao()

    @log
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

    @log
    def modify_card(self, card: Card, updates: dict) -> bool:
        """
        Modifie les champs spécifiés dans un dictionnaire d'une carte existante.

        Parameters
        ----------------
        card : Card
            Carte à modifier
        updates : dict
            Dictionnaire {colonne: nouvelle_valeur} à mettre à jour

        Returns
        ----------------
        bool
            True si la modification est un succès
            False sinon
        """
        print(f"Tentative de modification de la carte ID {card.id}...")
        success = self.dao.modify_card(card, updates)
        if success:
            print("Carte modifiée avec succès.")
        else:
            print("Échec de la modification.")
        return success
    
    @log
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

    @log
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
            raise ValueError(
                "Le nom de la carte doit être une chaîne de caractère non vide."
            )

        cartes_trouvees = self.dao.search_by_name(name)

        if not cartes_trouvees:
            print(f"Aucune carte trouvée pour '{name}'.")
            return []

        return cartes_trouvees

    @log
    def find_by_id(self, id):
        """
        

        Parameters
        ----------------
        id : int
            identifiant de la carte à rechercher.

        Returns
        ----------------
        card : Card
            objet Card correspondant au résultat de la recherche.
        """
        if not id or not isinstance(id, int):
            raise ValueError(
                "L'identifiant de la carte doit être un entier."
            )

        carte_trouvee = self.dao.find_by_id(id)

        if not carte_trouvee:
            print(f"Aucune carte trouvée pour l'identifiant '{id}'.")
            return []

        return carte_trouvee

    @log
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

    @log
    def random(self):
        """
        Récupérer une carte aléatoire

        Returns
        -------
        Card ou None
        """
        ids = self.dao.get_all_ids()
        if not ids:
            return None
        random_id = random.choice(ids)
        return self.dao.find_by_id(random_id)
