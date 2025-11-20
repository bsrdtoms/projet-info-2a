import uuid
from datetime import datetime
from typing import Optional


class Session:
    """Représente une session utilisateur active"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        last_activity: Optional[datetime] = None,
        is_active: bool = True
    ):
        """
        Initialise une session

        Parameters
        ----------
        session_id : str, optional
            Identifiant unique de session (généré automatiquement si None)
        user_id : int, optional
            ID de l'utilisateur
        created_at : datetime, optional
            Date de création
        last_activity : datetime, optional
            Dernière activité
        is_active : bool
            Session active ou non
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.last_activity = last_activity or datetime.now()
        self.is_active = is_active

    def update_activity(self):
        """Met à jour le timestamp de dernière activité"""
        self.last_activity = datetime.now()

    def __str__(self):
        return f"Session {self.session_id[:8]}... (user_id={self.user_id})"

    def __repr__(self):
        return f"Session(id='{self.session_id[:8]}...', user_id={self.user_id}, active={self.is_active})"