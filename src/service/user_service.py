import bcrypt
from dao.user_dao import UserDao
from dao.session_dao import SessionDao
from business_object.user import User, Client, create_user_from_type
from business_object.session import Session
from typing import Optional, Tuple


class UserService:
    """Service pour gérer les utilisateurs et l'authentification"""

    def __init__(self):
        self.user_dao = UserDao()
        self.session_dao = SessionDao()
        self.current_session: Optional[Session] = None

    def hash_password(self, password: str) -> str:
        """
        Hash un mot de passe avec bcrypt

        Parameters
        ----------
        password : str
            Mot de passe en clair

        Returns
        -------
        str
            Hash du mot de passe
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Vérifie qu'un mot de passe correspond au hash

        Parameters
        ----------
        password : str
            Mot de passe en clair
        password_hash : str
            Hash à vérifier

        Returns
        -------
        bool
            True si le mot de passe est correct
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def create_account(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_type: str = "client"
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Crée un nouveau compte utilisateur

        Parameters
        ----------
        email : str
            Email (doit être unique)
        password : str
            Mot de passe en clair (sera hashé)
        first_name : str, optional
            Prénom
        last_name : str, optional
            Nom
        user_type : str
            Type d'utilisateur ('client' par défaut)

        Returns
        -------
        tuple[bool, str, User | None]
            (succès, message, utilisateur créé)
        """
        # Validation email
        if not email or '@' not in email:
            return False, "Email invalide", None

        # Validation mot de passe
        if not password or len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères", None

        # Vérifier si l'email existe déjà
        existing_user = self.user_dao.find_by_email(email)
        if existing_user:
            return False, "Cet email est déjà utilisé", None

        # Créer l'utilisateur
        password_hash = self.hash_password(password)
        user = create_user_from_type(
            user_type=user_type,
            id=None,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )

        if self.user_dao.create(user):
            return True, f"Compte créé avec succès pour {email}", user
        else:
            return False, "Erreur lors de la création du compte", None

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Session]]:
        """
        Connecte un utilisateur

        Parameters
        ----------
        email : str
            Email
        password : str
            Mot de passe en clair

        Returns
        -------
        tuple[bool, str, Session | None]
            (succès, message, session créée)
        """
        # Trouver l'utilisateur
        user = self.user_dao.find_by_email(email)
        if not user:
            return False, "Email ou mot de passe incorrect", None

        # Vérifier le mot de passe
        if not self.verify_password(password, user.password_hash):
            return False, "Email ou mot de passe incorrect", None

        # Vérifier que le compte est actif
        if not user.is_active:
            return False, "Ce compte a été désactivé", None

        # Créer une session
        session = Session(user_id=user.id)
        if self.session_dao.create(session):
            self.current_session = session
            return True, f"Bienvenue {user.full_name}!", session
        else:
            return False, "Erreur lors de la connexion", None

    def logout(self) -> Tuple[bool, str]:
        """
        Déconnecte l'utilisateur courant

        Returns
        -------
        tuple[bool, str]
            (succès, message)
        """
        if not self.current_session:
            return False, "Aucune session active"

        if self.session_dao.deactivate(self.current_session.session_id):
            self.current_session = None
            return True, "Déconnexion réussie"
        else:
            return False, "Erreur lors de la déconnexion"

    def get_current_user(self) -> Optional[User]:
        """
        Récupère l'utilisateur actuellement connecté

        Returns
        -------
        User | None
            Utilisateur connecté ou None
        """
        if not self.current_session:
            return None
        return self.user_dao.find_by_id(self.current_session.user_id)

    def is_logged_in(self) -> bool:
        """Vérifie si un utilisateur est connecté"""
        return self.current_session is not None and self.current_session.is_active

    def delete_account(self, user_id: int) -> Tuple[bool, str]:
        """
        Supprime un compte utilisateur (admin uniquement)

        Parameters
        ----------
        user_id : int
            ID de l'utilisateur à supprimer

        Returns
        -------
        tuple[bool, str]
            (succès, message)
        """
        user = self.user_dao.find_by_id(user_id)
        if not user:
            return False, "Utilisateur introuvable"

        # Désactiver toutes les sessions
        self.session_dao.deactivate_all_user_sessions(user_id)

        # Supprimer l'utilisateur
        if self.user_dao.delete(user):
            return True, f"Compte {user.email} supprimé"
        else:
            return False, "Erreur lors de la suppression"

    def list_all_users(self):
        """Liste tous les utilisateurs (admin uniquement)"""
        return self.user_dao.list_all()

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Trouve un utilisateur par ID"""
        return self.user_dao.find_by_id(user_id)