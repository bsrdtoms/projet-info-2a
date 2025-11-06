# Fichier : src/dao/session_dao.py

from dao.db_connection import DBConnection
from business_object.session import Session
from typing import Optional, List
from datetime import datetime


class SessionDao:
    """Classe pour gérer les sessions en base de données"""

    def create(self, session: Session) -> bool:
        """
        Crée une nouvelle session

        Parameters
        ----------
        session : Session
            Session à créer

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
                        INSERT INTO project.sessions 
                        (session_id, user_id, created_at, last_activity, is_active)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            session.session_id,
                            session.user_id,
                            session.created_at,
                            session.last_activity,
                            session.is_active
                        )
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur création session: {e}")
            return False

    def find_by_id(self, session_id: str) -> Optional[Session]:
        """
        Trouve une session par son ID

        Parameters
        ----------
        session_id : str
            ID de la session

        Returns
        -------
        Session | None
            Session trouvée ou None
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT session_id, user_id, created_at, last_activity, is_active
                        FROM project.sessions
                        WHERE session_id = %s
                        """,
                        (session_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        return Session(
                            session_id=row['session_id'],
                            user_id=row['user_id'],
                            created_at=row['created_at'],
                            last_activity=row['last_activity'],
                            is_active=row['is_active']
                        )
            return None
        except Exception as e:
            print(f"❌ Erreur recherche session: {e}")
            return None

    def find_active_by_user_id(self, user_id: int) -> Optional[Session]:
        """
        Trouve la session active d'un utilisateur

        Parameters
        ----------
        user_id : int
            ID de l'utilisateur

        Returns
        -------
        Session | None
            Session active ou None
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT session_id, user_id, created_at, last_activity, is_active
                        FROM project.sessions
                        WHERE user_id = %s AND is_active = TRUE
                        ORDER BY last_activity DESC
                        LIMIT 1
                        """,
                        (user_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        return Session(
                            session_id=row['session_id'],
                            user_id=row['user_id'],
                            created_at=row['created_at'],
                            last_activity=row['last_activity'],
                            is_active=row['is_active']
                        )
            return None
        except Exception as e:
            print(f"❌ Erreur recherche session active: {e}")
            return None

    def update_activity(self, session_id: str) -> bool:
        """
        Met à jour la dernière activité d'une session

        Parameters
        ----------
        session_id : str
            ID de la session

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
                        UPDATE project.sessions
                        SET last_activity = %s
                        WHERE session_id = %s
                        """,
                        (datetime.now(), session_id)
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur mise à jour session: {e}")
            return False

    def deactivate(self, session_id: str) -> bool:
        """
        Désactive une session (logout)

        Parameters
        ----------
        session_id : str
            ID de la session

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
                        UPDATE project.sessions
                        SET is_active = FALSE
                        WHERE session_id = %s
                        """,
                        (session_id,)
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur désactivation session: {e}")
            return False

    def deactivate_all_user_sessions(self, user_id: int) -> bool:
        """
        Désactive toutes les sessions d'un utilisateur

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
                        """
                        UPDATE project.sessions
                        SET is_active = FALSE
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur désactivation sessions utilisateur: {e}")
            return False