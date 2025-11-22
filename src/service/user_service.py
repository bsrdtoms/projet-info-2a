import bcrypt
from dao.user_dao import UserDao
from dao.session_dao import SessionDao
from business_object.user import User, Client, create_user_from_type
from business_object.session import Session
from typing import Optional, Tuple
from utils.log_decorator import log


class UserService:
    """Service to manage users and authentication"""

    def __init__(self):
        self.user_dao = UserDao()
        self.session_dao = SessionDao()
        self.current_session: Optional[Session] = None

    @log
    def hash_password(self, password: str) -> str:
        """
        Hashes a password with bcrypt

        Parameters
        ----------
        password : str
            Plain text password

        Returns
        -------
        str
            Password hash
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @log
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifies that a password matches the hash

        Parameters
        ----------
        password : str
            Plain text password
        password_hash : str
            Hash to verify

        Returns
        -------
        bool
            True if the password is correct
        """
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @log
    def create_account(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_type: str = "client",
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Creates a new user account

        Parameters
        ----------
        email : str
            Email (must be unique)
        password : str
            Plain text password (will be hashed)
        first_name : str, optional
            First name
        last_name : str, optional
            Last name
        user_type : str
            User type ('client' by default)

        Returns
        -------
        tuple[bool, str, User | None]
            (success, message, created user)
        """
        # Email validation
        if not email or "@" not in email:
            return False, "Invalid email", None

        # Password validation
        if not password or len(password) < 6:
            return False, "Password must contain at least 6 characters", None

        # Check if email already exists
        existing_user = self.user_dao.find_by_email(email)
        if existing_user:
            return False, "This email is already in use", None

        # Create the user
        password_hash = self.hash_password(password)
        user = create_user_from_type(
            user_type=user_type,
            id=None,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
        )

        if self.user_dao.create(user):
            return True, f"Account successfully created for {email}", user
        else:
            return False, "Error creating account", None

    @log
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Session]]:
        """
        Logs in a user

        Parameters
        ----------
        email : str
            Email
        password : str
            Plain text password

        Returns
        -------
        tuple[bool, str, Session | None]
            (success, message, created session)
        """
        # Find the user
        user = self.user_dao.find_by_email(email)
        if not user:
            return False, "Incorrect email or password", None

        # Verify the password
        if not self.verify_password(password, user.password_hash):
            return False, "Incorrect email or password", None

        # Check that the account is active
        if not user.is_active:
            return False, "This account has been deactivated", None

        # Create a session
        session = Session(user_id=user.id)
        if self.session_dao.create(session):
            self.current_session = session
            return True, f"Welcome {user.full_name}!", session
        else:
            return False, "Error during login", None

    @log
    def logout(self) -> Tuple[bool, str]:
        """
        Logs out the current user

        Returns
        -------
        tuple[bool, str]
            (success, message)
        """
        if not self.current_session:
            return False, "No active session"

        if self.session_dao.deactivate(self.current_session.session_id):
            self.current_session = None
            return True, "Successfully logged out"
        else:
            return False, "Error during logout"

    @log
    def get_current_user(self) -> Optional[User]:
        """
        Retrieves the currently logged in user

        Returns
        -------
        User | None
            Logged in user or None
        """
        if not self.current_session:
            return None
        return self.user_dao.find_by_id(self.current_session.user_id)

    @log
    def delete_account(self, user_id: int) -> Tuple[bool, str]:
        """
        Deletes a user account (admin only)

        Parameters
        ----------
        user_id : int
            ID of the user to delete

        Returns
        -------
        tuple[bool, str]
            (success, message)
        """
        user = self.user_dao.find_by_id(user_id)
        if not user:
            return False, "User not found"

        # Deactivate all sessions
        self.session_dao.deactivate_all_user_sessions(user_id)

        # Delete the user
        if self.user_dao.delete(user):
            return True, f"Account {user.email} deleted"
        else:
            return False, "Error during deletion"

    # Add to src/service/user_service.py
    @log
    def update_user(
        self,
        user_id: int,
        user_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Tuple[bool, str, dict]:
        """Update a user (admin only)"""
        user = self.user_dao.find_by_id(user_id)
        if not user:
            return False, "User not found", {}

        updates = {}
        if user_type is not None:
            if user_type not in ["client", "game_designer", "admin"]:
                return False, "Invalid user type", {}
            user.user_type = user_type
            updates["user_type"] = user_type

        if is_active is not None:
            user.is_active = is_active
            updates["is_active"] = is_active

        if first_name is not None:
            user.first_name = first_name
            updates["first_name"] = first_name

        if last_name is not None:
            user.last_name = last_name
            updates["last_name"] = last_name

        if not updates:
            return False, "No updates provided", {}

        if self.user_dao.update(user):
            return True, f"User {user.email} updated", updates
        return False, "Error updating user", {}

    @log
    def list_all_users(self):
        """Lists all users (admin only)"""
        return self.user_dao.list_all()

    @log
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Finds a user by ID"""
        return self.user_dao.find_by_id(user_id)

    @log
    def find_by_email(self, email: str) -> Optional[User]:
        """Finds a user by email"""
        return self.user_dao.find_by_email(email)
