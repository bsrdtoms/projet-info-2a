from dao.db_connection import DBConnection
from business_object.user import User, create_user_from_type
from typing import Optional, List
from utils.log_decorator import log


class UserDao:
    """Class to access users in the database"""

    @log
    def create(self, user: User) -> bool:
        """
        Creates a new user in the database

        Parameters
        ----------
        user : User
            User to create

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
                        INSERT INTO project.users 
                        (email, password_hash, first_name, last_name, user_type, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            user.email,
                            user.password_hash,
                            user.first_name,
                            user.last_name,
                            user.user_type,
                            user.is_active
                        )
                    )
                    user.id = cursor.fetchone()['id']
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return False

    @log
    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Finds a user by their ID

        Parameters
        ----------
        user_id : int
            User ID

        Returns
        -------
        User | None
            User found or None
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, email, password_hash, first_name, last_name,
                               user_type, is_active, created_at, updated_at
                        FROM project.users
                        WHERE id = %s
                        """,
                        (user_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        return create_user_from_type(
                            user_type=row['user_type'],
                            id=row['id'],
                            email=row['email'],
                            password_hash=row['password_hash'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            is_active=row['is_active'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        )
            return None
        except Exception as e:
            print(f"❌ Error searching for user: {e}")
            return None

    @log
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Finds a user by their email

        Parameters
        ----------
        email : str
            User email

        Returns
        -------
        User | None
            User found or None
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, email, password_hash, first_name, last_name,
                               user_type, is_active, created_at, updated_at
                        FROM project.users
                        WHERE email = %s
                        """,
                        (email,)
                    )
                    row = cursor.fetchone()
                    if row:
                        return create_user_from_type(
                            user_type=row['user_type'],
                            id=row['id'],
                            email=row['email'],
                            password_hash=row['password_hash'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            is_active=row['is_active'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        )
            return None
        except Exception as e:
            print(f"❌ Error searching for user by email: {e}")
            return None

    @log
    def list_all(self) -> List[User]:
        """
        Lists all users

        Returns
        -------
        list[User]
            List of all users
        """
        users = []
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, email, password_hash, first_name, last_name,
                               user_type, is_active, created_at, updated_at
                        FROM project.users
                        ORDER BY created_at DESC
                        """
                    )
                    for row in cursor.fetchall():
                        user = create_user_from_type(
                            user_type=row['user_type'],
                            id=row['id'],
                            email=row['email'],
                            password_hash=row['password_hash'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            is_active=row['is_active'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        )
                        users.append(user)
        except Exception as e:
            print(f"❌ Error listing users: {e}")
        return users

    @log
    def delete(self, user: User) -> bool:
        """
        Deletes a user

        Parameters
        ----------
        user : User
            User to delete

        Returns
        -------
        bool
            True if success, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM project.users WHERE id = %s",
                        (user.id,)
                    )
                    deleted = cursor.rowcount > 0
                connection.commit()
            return deleted
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
            return False

    @log
    def update(self, user: User) -> bool:
        """
        Updates a user

        Parameters
        ----------
        user : User
            User with new data

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
                        UPDATE project.users
                        SET first_name = %s, last_name = %s, 
                            is_active = %s
                        WHERE id = %s
                        """,
                        (user.first_name, user.last_name, user.is_active, user.id)
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False