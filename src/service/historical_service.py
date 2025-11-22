from dao.historical_dao import HistoricalDao
from business_object.historical_search import HistoricalSearch
from typing import List, Optional


class HistoricalService:
    """Service to manage search history"""

    def __init__(self):
        self.dao = HistoricalDao()

    def add_search(
        self,
        user_id: int,
        query_text: str,
        query_embedding: Optional[list] = None,
        result_count: Optional[int] = None,
    ) -> bool:
        """Adds a search to the history"""
        search = HistoricalSearch(
            id=None,
            user_id=user_id,
            query_text=query_text,
            query_embedding=query_embedding,
            result_count=result_count,
        )
        return self.dao.create(search)

    def get_user_history(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> List[HistoricalSearch]:
        """Retrieves a user's history"""
        return self.dao.find_by_user_id(user_id, limit, offset)

    def get_history_count(self, user_id: int) -> int:
        """Counts the number of searches"""
        return self.dao.count_by_user_id(user_id)

    def delete_search(self, search_id: int) -> bool:
        """Deletes a specific search by its ID"""
        return self.dao.delete_by_id(search_id)

    def clear_user_history(self, user_id: int) -> bool:
        """Clears all of a user's history"""
        return self.dao.delete_all_by_user_id(user_id)

    def get_paginated_history(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> dict:
        """Retrieves history with pagination"""
        offset = (page - 1) * per_page
        searches = self.dao.find_by_user_id(user_id, limit=per_page, offset=offset)
        total = self.dao.count_by_user_id(user_id)
        total_pages = (total + per_page - 1) // per_page

        return {
            "searches": searches,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        }

    def get_stats(self, user_id: int) -> dict:
        """Retrieves search statistics for a user"""
        searches = self.dao.find_by_user_id(user_id, limit=1000)  # Get all searches

        if not searches:
            return {
                "total_searches": 0,
                "total_results": 0,
                "avg_results": 0,
                "most_recent": None,
                "oldest": None,
            }

        total_searches = len(searches)
        total_results = sum(s.result_count for s in searches if s.result_count)
        avg_results = total_results / total_searches if total_searches > 0 else 0

        # Searches are already ordered by created_at DESC
        most_recent = searches[0].created_at
        oldest = searches[-1].created_at

        return {
            "total_searches": total_searches,
            "total_results": total_results,
            "avg_results": avg_results,
            "most_recent": most_recent,
            "oldest": oldest,
        }
