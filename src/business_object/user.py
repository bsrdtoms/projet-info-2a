# File: src/business_object/user.py
# REPLACE EMPTY CONTENT

from datetime import datetime
from typing import Optional


class User:
    """Base class for all user types"""

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
        """Returns the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def __str__(self):
        return f"{self.user_type.capitalize()} - {self.full_name} ({self.email})"

    def __repr__(self):
        return f"User(id={self.id}, email='{self.email}', type='{self.user_type}')"