from datetime import datetime
from typing import Optional


class User:
    """Classe de base pour tous les types d'utilisateurs"""

    def __init__(
        self,
        id: Optional[int],
        email: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_type: str = "client",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un utilisateur

        Parameters
        ----------
        id : int | None
            Identifiant unique (None avant insertion en base)
        email : str
            Email unique de l'utilisateur
        password_hash : str
            Hash du mot de passe (jamais le mot de passe en clair!)
        first_name : str, optional
            Prénom
        last_name : str, optional
            Nom de famille
        user_type : str
            Type d'utilisateur ('client', 'game_designer', 'admin')
        is_active : bool
            Compte actif ou non
        created_at : datetime, optional
            Date de création
        updated_at : datetime, optional
            Date de dernière modification
        """
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.user_type = user_type
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @property
    def full_name(self) -> str:
        """Retourne le nom complet de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def __str__(self):
        return f"{self.user_type.capitalize()} - {self.full_name} ({self.email})"

    def __repr__(self):
        return f"User(id={self.id}, email='{self.email}', type='{self.user_type}')"


class Client(User):
    """Utilisateur classique pouvant rechercher des cartes et gérer des favoris"""

    def __init__(self, **kwargs):
        kwargs['user_type'] = 'client'
        super().__init__(**kwargs)


class GameDesigner(User):
    """Utilisateur pouvant gérer les cartes (ajout, modification, suppression)"""

    def __init__(self, **kwargs):
        kwargs['user_type'] = 'game_designer'
        super().__init__(**kwargs)


class Admin(User):
    """Administrateur pouvant gérer les utilisateurs"""

    def __init__(self, **kwargs):
        kwargs['user_type'] = 'admin'
        super().__init__(**kwargs)


# Factory pattern pour créer le bon type d'utilisateur
def create_user_from_type(user_type: str, **kwargs) -> User:
    """
    Factory pour créer le bon type d'utilisateur selon user_type

    Parameters
    ----------
    user_type : str
        'client', 'game_designer', ou 'admin'
    **kwargs
        Autres paramètres à passer au constructeur

    Returns
    -------
    User
        Instance de Client, GameDesigner ou Admin
    """
    user_classes = {
        'client': Client,
        'game_designer': GameDesigner,
        'admin': Admin
    }

    user_class = user_classes.get(user_type, Client)
    return user_class(**kwargs)