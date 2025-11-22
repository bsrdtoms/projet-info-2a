from datetime import datetime
from typing import Optional


class HistoricalSearch:
    """Represents a search in a user's history"""

    def __init__(
        self,
        id: Optional[int],
        user_id: int,
        query_text: str,
        query_embedding: Optional[list] = None,
        result_count: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.query_text = query_text
        self.query_embedding = query_embedding
        self.result_count = result_count
        self.created_at = created_at or datetime.now()

    def __str__(self):
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"[{date_str}] '{self.query_text}' ({self.result_count} results)"

    def __repr__(self):
        return (
            f"HistoricalSearch(id={self.id}, user_id={self.user_id}, "
            f"query='{self.query_text[:30]}...', results={self.result_count})"
        )
