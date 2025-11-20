from technical_components.embedding.ollama_embedding import get_embedding
from utils.log_decorator import log
from business_object.historical_search import HistoricalSearch
from dao.historical_dao import HistoricalSearchDAO

class HistoricalSearchService:
    """Service pour gérer l'historique des recherches"""

    def __init__(self):
        self.dao = HistoricalSearchDAO()

    @log
    def add_search(self, user_id: int, query_text: str, result_count: int,
                   save_embedding: bool = True) -> bool:
        """
        Enregistre une nouvelle recherche dans l'historique

        Parameters
        ----------
        user_id : int
            ID de l'utilisateur
        query_text : str
            Texte de la requête
        result_count : int
            Nombre de résultats trouvés
        save_embedding : bool
            Si True, génère et sauvegarde l'embedding de la requête

        Returns
        -------
        bool
            True si succès, False sinon
        """
        try:
            query_embedding = None

            if save_embedding and query_text:
                embedding_response = get_embedding(query_text)
                query_embedding = embedding_response.get("embeddings", [None])[0]

            historical_search = HistoricalSearch(
                user_id=user_id,
                query_text=query_text,
                query_embedding=query_embedding,
                result_count=result_count
            )

            return self.dao.add(historical_search)

        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement: {e}")
            return False

    @log
    def get_history(self, user_id: int, limit: int = 50) -> list[HistoricalSearch]:
        """
        Récupère l'historique de recherche d'un utilisateur

        Parameters
        ----------
        user_id : int
            ID de l'utilisateur
        limit : int
            Nombre maximum de résultats

        Returns
        -------
        list[HistoricalSearch]
            Liste des recherches historiques
        """
        return self.dao.read_history(user_id, limit)

    @log
    def delete_search(self, search_id: int) -> bool:
        """Supprime une recherche spécifique"""
        return self.dao.delete_search(search_id)

    @log
    def clear_history(self, user_id: int) -> bool:
        """Supprime tout l'historique d'un utilisateur"""
        return self.dao.clear_user_history(user_id)

    @log
    def get_stats(self, user_id: int) -> dict:
        """Récupère les statistiques de recherche d'un utilisateur"""
        return self.dao.get_user_search_stats(user_id)