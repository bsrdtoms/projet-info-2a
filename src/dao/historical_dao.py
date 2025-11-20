from dao.db_connection import DBConnection
from utils.log_decorator import log
from business_object.historical_search import HistoricalSearch

class HistoricalSearchDAO:
    """DAO pour gérer l'historique des recherches en base de données"""

    @log
    def add(self, historical_search: HistoricalSearch) -> bool:
        """
        Ajoute une nouvelle entrée d'historique

        Parameters
        ----------
        historical_search : HistoricalSearch
            Objet historique à ajouter

        Returns
        -------
        bool
            True si succès, False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO project.search_history
                        (user_id, query_text, query_embedding, result_count, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            historical_search.user_id,
                            historical_search.query_text,
                            historical_search.query_embedding,
                            historical_search.result_count,
                            historical_search.created_at
                        )
                    )
                    historical_search.id = cursor.fetchone()['id']
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout à l'historique: {e}")
            return False

    @log
    def read_history(self, user_id: int, limit: int = 50) -> list[HistoricalSearch]:
        """
        Récupère l'historique de recherche d'un utilisateur

        Parameters
        ----------
        user_id : int
            ID de l'utilisateur
        limit : int
            Nombre maximum de résultats (par défaut 50)

        Returns
        -------
        list[HistoricalSearch]
            Liste des recherches historiques
        """
        query = """
            SELECT id, user_id, query_text, query_embedding, result_count, created_at
            FROM project.search_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        historical_searches = []

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (user_id, limit))
                    rows = cursor.fetchall()

                    for row in rows:
                        search = HistoricalSearch(
                            id=row['id'],
                            user_id=row['user_id'],
                            query_text=row['query_text'],
                            query_embedding=row['query_embedding'],
                            result_count=row['result_count'],
                            created_at=row['created_at']
                        )
                        historical_searches.append(search)

        except Exception as e:
            print(f"❌ Erreur lors de la lecture de l'historique: {e}")
            raise

        return historical_searches

    @log
    def delete_search(self, search_id: int) -> bool:
        """
        Supprime une entrée d'historique spécifique

        Parameters
        ----------
        search_id : int
            ID de l'entrée à supprimer

        Returns
        -------
        bool
            True si succès, False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM project.search_history WHERE id = %s",
                        (search_id,)
                    )
                    deleted = cursor.rowcount > 0
                connection.commit()
            return deleted
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False

    @log
    def clear_user_history(self, user_id: int) -> bool:
        """
        Supprime tout l'historique d'un utilisateur

        Parameters
        ----------
        user_id : int
            ID de l'utilisateur

        Returns
        -------
        bool
            True si succès, False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM project.search_history WHERE user_id = %s",
                        (user_id,)
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de l'historique: {e}")
            return False

    @log
    def get_user_search_stats(self, user_id: int) -> dict:
        """
        Récupère des statistiques sur les recherches d'un utilisateur

        Parameters
        ----------
        user_id : int
            ID de l'utilisateur

        Returns
        -------
        dict
            Dictionnaire avec statistiques (total_searches, avg_results, most_recent, etc.)
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            COUNT(*) as total_searches,
                            AVG(result_count) as avg_results,
                            MAX(created_at) as most_recent,
                            MIN(created_at) as oldest,
                            SUM(result_count) as total_results
                        FROM project.search_history
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                    row = cursor.fetchone()

                    if row:
                        return {
                            'total_searches': row['total_searches'] or 0,
                            'avg_results': float(row['avg_results']) if row['avg_results'] else 0,
                            'most_recent': row['most_recent'],
                            'oldest': row['oldest'],
                            'total_results': row['total_results'] or 0
                        }
                    return {}

        except Exception as e:
            print(f"❌ Erreur lors de la récupération des statistiques: {e}")
            raise


