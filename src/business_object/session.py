import uuid
from datetime import datetime
from typing import Optional


class Session:
    """Represents an active user session"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        last_activity: Optional[datetime] = None,
        is_active: bool = True
    ):
        """
        Initialize a session

        Parameters
        ----------
        session_id : str, optional
            Unique session identifier (automatically generated if None)
        user_id : int, optional
            User ID
        created_at : datetime, optional
            Creation date
        last_activity : datetime, optional
            Last activity
        is_active : bool
            Whether session is active or not
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.last_activity = last_activity or datetime.now()
        self.is_active = is_active

    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = datetime.now()

    def __str__(self):
        return f"Session {self.session_id[:8]}... (user_id={self.user_id})"

    def __repr__(self):
        return f"Session(id='{self.session_id[:8]}...', user_id={self.user_id}, active={self.is_active})"