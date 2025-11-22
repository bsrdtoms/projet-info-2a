import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from dao.session_dao import SessionDao
from business_object.session import Session


class TestSessionDao:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with patch("dao.session_dao.DBConnection") as mock_db_connection:
            self.mock_connection = MagicMock()
            self.mock_cursor = MagicMock()

            self.mock_connection.__enter__ = Mock(return_value=self.mock_connection)
            self.mock_connection.__exit__ = Mock(return_value=None)
            self.mock_connection.cursor.return_value.__enter__ = Mock(
                return_value=self.mock_cursor
            )
            self.mock_connection.cursor.return_value.__exit__ = Mock(return_value=None)

            mock_db_connection.return_value.connection = self.mock_connection
            yield

    def test_create_success(self):
        # GIVEN
        session = Session(
            session_id="test-session-123",
            user_id=1,
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_activity=datetime(2024, 1, 1, 10, 0, 0),
            is_active=True,
        )
        dao = SessionDao()

        # WHEN
        result = dao.create(session)

        # THEN
        assert result is True
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_create_failure(self):
        # GIVEN
        session = Session(
            session_id="test-session-123",
            user_id=1,
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            last_activity=datetime(2024, 1, 1, 10, 0, 0),
            is_active=True,
        )
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = SessionDao()

        # WHEN
        result = dao.create(session)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()

    def test_find_by_id_success(self):
        # GIVEN
        session_id = "test-session-123"
        expected_session_data = {
            "session_id": "test-session-123",
            "user_id": 1,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "last_activity": datetime(2024, 1, 1, 10, 30, 0),
            "is_active": True,
        }
        self.mock_cursor.fetchone.return_value = expected_session_data
        dao = SessionDao()

        # WHEN
        result = dao.find_by_id(session_id)

        # THEN
        assert result is not None
        assert isinstance(result, Session)
        assert result.session_id == "test-session-123"
        assert result.user_id == 1
        assert result.is_active is True

    def test_find_by_id_not_found(self):
        # GIVEN
        session_id = "non-existent-session"
        self.mock_cursor.fetchone.return_value = None
        dao = SessionDao()

        # WHEN
        result = dao.find_by_id(session_id)

        # THEN
        assert result is None

    def test_find_by_id_database_error(self):
        # GIVEN
        session_id = "test-session-123"
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = SessionDao()

        # WHEN
        result = dao.find_by_id(session_id)

        # THEN
        assert result is None

    def test_find_active_by_user_id_success(self):
        # GIVEN
        user_id = 1
        expected_session_data = {
            "session_id": "active-session-123",
            "user_id": 1,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "last_activity": datetime(2024, 1, 1, 11, 0, 0),
            "is_active": True,
        }
        self.mock_cursor.fetchone.return_value = expected_session_data
        dao = SessionDao()

        # WHEN
        result = dao.find_active_by_user_id(user_id)

        # THEN
        assert result is not None
        assert result.session_id == "active-session-123"
        assert result.user_id == 1
        assert result.is_active is True

    def test_find_active_by_user_id_not_found(self):
        # GIVEN
        user_id = 999
        self.mock_cursor.fetchone.return_value = None
        dao = SessionDao()

        # WHEN
        result = dao.find_active_by_user_id(user_id)

        # THEN
        assert result is None

    def test_find_active_by_user_id_database_error(self):
        # GIVEN
        user_id = 1
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = SessionDao()

        # WHEN
        result = dao.find_active_by_user_id(user_id)

        # THEN
        assert result is None

    def test_update_activity_success(self):
        # GIVEN
        session_id = "test-session-123"
        dao = SessionDao()

        with patch("dao.session_dao.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            # WHEN
            result = dao.update_activity(session_id)

            # THEN
            assert result is True
            self.mock_cursor.execute.assert_called_once()
            self.mock_connection.commit.assert_called_once()

    def test_update_activity_failure(self):
        # GIVEN
        session_id = "test-session-123"
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = SessionDao()

        # WHEN
        result = dao.update_activity(session_id)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()

    def test_deactivate_success(self):
        # GIVEN
        session_id = "test-session-123"
        dao = SessionDao()

        # WHEN
        result = dao.deactivate(session_id)

        # THEN
        assert result is True
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_deactivate_failure(self):
        # GIVEN
        session_id = "test-session-123"
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = SessionDao()

        # WHEN
        result = dao.deactivate(session_id)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()

    def test_deactivate_all_user_sessions_success(self):
        # GIVEN
        user_id = 1
        dao = SessionDao()

        # WHEN
        result = dao.deactivate_all_user_sessions(user_id)

        # THEN
        assert result is True
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_deactivate_all_user_sessions_failure(self):
        # GIVEN
        user_id = 1
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = SessionDao()

        # WHEN
        result = dao.deactivate_all_user_sessions(user_id)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()
