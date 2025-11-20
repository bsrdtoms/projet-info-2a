# ============================================================
# BUSINESS OBJECT: HistoricalSearch
# ============================================================

from datetime import datetime
from typing import Optional


class HistoricalSearch:
    """Représente une recherche historique d'un utilisateur"""

    def __init__(
        self,
        id: Optional[int] = None,
        user_id: int = None,
        query_text: str = None,
        query_embedding: list[float] = None,
        result_count: int = 0,
        created_at: Optional[datetime] = None
    ):
        """
        Initialise une recherche historique

        Parameters
        ----------
        id : int, optional
            ID unique de l'enregistrement historique
        user_id : int
            ID de l'utilisateur qui a effectué la recherche
        query_text : str
            Texte de la requête de recherche
        query_embedding : list[float], optional
            Embedding de la requête
        result_count : int
            Nombre de résultats trouvés
        created_at : datetime, optional
            Date/heure de la recherche
        """
        self.id = id
        self.user_id = user_id
        self.query_text = query_text
        self.query_embedding = query_embedding
        self.result_count = result_count
        self.created_at = created_at or datetime.now()

    def __str__(self):
        return f"Search #{self.id}: '{self.query_text}' - {self.result_count} results ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    def __repr__(self):
        return f"HistoricalSearch(id={self.id}, user_id={self.user_id}, query='{self.query_text[:30]}...', results={self.result_count})"
