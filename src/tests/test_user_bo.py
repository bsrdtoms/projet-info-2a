# tests/test_user_bo.py
import pytest
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from business_object.user import (
    User,
    Client,
    GameDesigner,
    Admin,
    create_user_from_type,
)


class TestUser:
    def test_user_init_basic(self):
        email = "test@example.com"
        password_hash = "hashed_password"
        first_name = "John"
        last_name = "Doe"

        user = User(
            id=1,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            user_type="client",
            is_active=True,
        )

        assert user.id == 1
        assert user.email == email
        assert user.password_hash == password_hash
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.user_type == "client"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.full_name == f"{first_name} {last_name}"
        assert str(user) == f"Client - {first_name} {last_name} ({email})"

    def test_user_full_name_fallback(self):
        email = "test@example.com"
        password_hash = "hashed_password"
        user = User(id=2, email=email, password_hash=password_hash)
        assert user.full_name == email
        assert str(user) == f"Client - {email} ({email})"

    def test_subclasses_types(self):
        client = Client(id=1, email="c@example.com", password_hash="hash")
        designer = GameDesigner(id=2, email="d@example.com", password_hash="hash")
        admin = Admin(id=3, email="a@example.com", password_hash="hash")

        assert client.user_type == "client"
        assert designer.user_type == "game_designer"
        assert admin.user_type == "admin"

    def test_factory_creates_correct_type(self):
        kwargs = {"id": 1, "email": "x@example.com", "password_hash": "hash"}

        user1 = create_user_from_type("client", **kwargs)
        user2 = create_user_from_type("game_designer", **kwargs)
        user3 = create_user_from_type("admin", **kwargs)
        user_default = create_user_from_type("unknown_type", **kwargs)

        assert isinstance(user1, Client)
        assert isinstance(user2, GameDesigner)
        assert isinstance(user3, Admin)
        assert isinstance(user_default, Client)

    def test_repr_str_methods(self):
        user = User(
            id=10,
            email="repr@example.com",
            password_hash="hash",
            first_name="R",
            last_name="E",
        )
        assert repr(user) == "User(id=10, email='repr@example.com', type='client')"
        assert "R E" in str(user)
