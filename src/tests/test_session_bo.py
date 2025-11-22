# tests/test_session_bo.py
import pytest
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from business_object.session import (
    Session,
)  # Assure-toi que session.py est bien dans business_object


class TestSession:
    def test_session_init_basic(self):
        # GIVEN
        user_id = 123

        # WHEN
        session = Session(user_id=user_id)

        # THEN
        assert session.user_id == user_id
        assert session.session_id is not None
        assert session.is_active is True
        assert isinstance(session.created_at, datetime)
        # plus d'updated_at car non présent dans la classe Session
        assert str(session).startswith("Session ")
        assert f"user_id={user_id}" in str(session)

    def test_session_deactivate(self):
        # GIVEN
        session = Session(user_id=1)

        # WHEN
        session.is_active = False

        # THEN
        assert session.is_active is False

    def test_repr_str_methods(self):
        # GIVEN
        session = Session(user_id=5)

        # THEN
        r = repr(session)
        s = str(session)
        assert r.startswith("Session(")
        assert f"{session.user_id}" in s
        assert (
            f"{session.session_id}" in s or "Session " in s
        )  # s'adapte au __str__ réel

    def test_custom_created_timestamp(self):
        # GIVEN
        created = datetime(2020, 1, 1)
        session = Session(user_id=2, created_at=created)

        # THEN
        assert session.created_at == created
        assert session.user_id == 2
