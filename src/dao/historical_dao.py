from dao.db_connection import DBConnection
from business_object.historical_search import HistoricalSearch
from typing import List


class HistoricalDao:
    """Class to access search history in the database"""

    def create(self, historical_search: HistoricalSearch) -> bool:
        """Adds a search to the history"""
        try:
            embedding_str = None
            if historical_search.query_embedding:
                embedding_str = (
                    "[" + ",".join(str(f) for f in historical_search.query_embedding) + "]"
                )

            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO project.search_history 
                        (user_id, query_text, query_embedding, result_count, created_at)
                        VALUES (%s, %s, %s::vector, %s, %s)
                        RETURNING id
                        """,
                        (
                            historical_search.user_id,
                            historical_search.query_text,
                            embedding_str,
                            historical_search.result_count,
                            historical_search.created_at,
                        ),
                    )
                    historical_search.id = cursor.fetchone()["id"]
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error adding to history: {e}")
            return False

    def find_by_user_id(self, user_id: int, limit: int = 50, offset: int = 0) -> List[HistoricalSearch]:
        """Retrieves the history of a user"""
        searches = []
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, user_id, query_text, query_embedding, 
                               result_count, created_at
                        FROM project.search_history
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (user_id, limit, offset),
                    )
                    for row in cursor.fetchall():
                        search = HistoricalSearch(
                            id=row["id"],
                            user_id=row["user_id"],
                            query_text=row["query_text"],
                            query_embedding=row["query_embedding"],
                            result_count=row["result_count"],
                            created_at=row["created_at"],
                        )
                        searches.append(search)
        except Exception as e:
            print(f"❌ Error retrieving history: {e}")
        return searches

    def count_by_user_id(self, user_id: int) -> int:
        """Counts the number of searches for a user"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT COUNT(*) as count
                        FROM project.search_history
                        WHERE user_id = %s
                        """,
                        (user_id,),
                    )
                    return cursor.fetchone()["count"]
        except Exception as e:
            print(f"❌ Error counting history: {e}")
            return 0

    def delete_by_id(self, search_id: int) -> bool:
        """Deletes a specific search by its ID"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM project.search_history WHERE id = %s",
                        (search_id,),
                    )
                    deleted = cursor.rowcount > 0
                connection.commit()
            return deleted
        except Exception as e:
            print(f"❌ Error deleting search: {e}")
            return False

    def delete_all_by_user_id(self, user_id: int) -> bool:
        """Deletes all history for a user"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM project.search_history WHERE user_id = %s",
                        (user_id,),
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error deleting history: {e}")
            return False