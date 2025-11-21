from dao.db_connection import DBConnection
from business_object.session import Session
from typing import Optional, List
from datetime import datetime
from utils.log_decorator import log


class SessionDao:
    """Class to manage sessions in the database"""

    @log
    def create(self, session: Session) -> bool:
        """
        Creates a new session

        Parameters
        ----------
        session : Session
            Session to create

        Returns
        -------
        bool
            True if success, False otherwise
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
            print(f"❌ Error creating session: {e}")
            return False

    @log
    def find_by_id(self, session_id: str) -> Optional[Session]:
        """
        Finds a session by its ID

        Parameters
        ----------
        session_id : str
            Session ID

        Returns
        -------
        Session | None
            Session found or None
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
            print(f"❌ Error searching for session: {e}")
            return None

    @log
    def find_active_by_user_id(self, user_id: int) -> Optional[Session]:
        """
        Finds the active session of a user

        Parameters
        ----------
        user_id : int
            User ID

        Returns
        -------
        Session | None
            Active session or None
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
            print(f"❌ Error searching for active session: {e}")
            return None

    @log
    def update_activity(self, session_id: str) -> bool:
        """
        Updates the last activity of a session

        Parameters
        ----------
        session_id : str
            Session ID

        Returns
        -------
        bool
            True if success, False otherwise
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
            print(f"❌ Error updating session: {e}")
            return False

    @log
    def deactivate(self, session_id: str) -> bool:
        """
        Deactivates a session (logout)

        Parameters
        ----------
        session_id : str
            Session ID

        Returns
        -------
        bool
            True if success, False otherwise
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
            print(f"❌ Error deactivating session: {e}")
            return False

    @log
    def deactivate_all_user_sessions(self, user_id: int) -> bool:
        """
        Deactivates all sessions of a user

        Parameters
        ----------
        user_id : int
            User ID

        Returns
        -------
        bool
            True if success, False otherwise
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
            print(f"❌ Error deactivating user sessions: {e}")
            return False