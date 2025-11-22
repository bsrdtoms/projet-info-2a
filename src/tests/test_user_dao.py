import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from dao.user_dao import UserDao
from business_object.user import User, create_user_from_type


class TestUserDao:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with patch("dao.user_dao.DBConnection") as mock_db_connection:
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
        user = User(
            id=None,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            user_type="student",
            is_active=True,
        )
        self.mock_cursor.fetchone.return_value = {"id": 1}
        dao = UserDao()

        # WHEN
        result = dao.create(user)

        # THEN
        assert result is True
        assert user.id == 1
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_create_failure(self):
        # GIVEN
        user = User(
            id=None,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            user_type="student",
            is_active=True,
        )
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = UserDao()

        # WHEN
        result = dao.create(user)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()

    def test_find_by_id_success(self):
        # GIVEN
        user_id = 1
        expected_user_data = {
            "id": 1,
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "student",
            "is_active": True,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "updated_at": datetime(2024, 1, 1, 10, 0, 0),
        }
        self.mock_cursor.fetchone.return_value = expected_user_data

        with patch("dao.user_dao.create_user_from_type") as mock_create_user:
            mock_create_user.return_value = User(
                id=1,
                email="test@example.com",
                password_hash="hashed_password",
                first_name="John",
                last_name="Doe",
                user_type="student",
                is_active=True,
            )
            dao = UserDao()

            # WHEN
            result = dao.find_by_id(user_id)

            # THEN
            assert result is not None
            assert isinstance(result, User)
            mock_create_user.assert_called_once_with(
                user_type="student",
                id=1,
                email="test@example.com",
                password_hash="hashed_password",
                first_name="John",
                last_name="Doe",
                is_active=True,
                created_at=datetime(2024, 1, 1, 10, 0, 0),
                updated_at=datetime(2024, 1, 1, 10, 0, 0),
            )

    def test_find_by_id_not_found(self):
        # GIVEN
        user_id = 999
        self.mock_cursor.fetchone.return_value = None
        dao = UserDao()

        # WHEN
        result = dao.find_by_id(user_id)

        # THEN
        assert result is None

    def test_find_by_id_database_error(self):
        # GIVEN
        user_id = 1
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = UserDao()

        # WHEN
        result = dao.find_by_id(user_id)

        # THEN
        assert result is None

    def test_find_by_email_success(self):
        # GIVEN
        email = "test@example.com"
        expected_user_data = {
            "id": 1,
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "student",
            "is_active": True,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "updated_at": datetime(2024, 1, 1, 10, 0, 0),
        }
        self.mock_cursor.fetchone.return_value = expected_user_data

        with patch("dao.user_dao.create_user_from_type") as mock_create_user:
            mock_create_user.return_value = User(
                id=1,
                email="test@example.com",
                password_hash="hashed_password",
                first_name="John",
                last_name="Doe",
                user_type="student",
                is_active=True,
            )
            dao = UserDao()

            # WHEN
            result = dao.find_by_email(email)

            # THEN
            assert result is not None
            assert isinstance(result, User)
            mock_create_user.assert_called_once_with(
                user_type="student",
                id=1,
                email="test@example.com",
                password_hash="hashed_password",
                first_name="John",
                last_name="Doe",
                is_active=True,
                created_at=datetime(2024, 1, 1, 10, 0, 0),
                updated_at=datetime(2024, 1, 1, 10, 0, 0),
            )

    def test_find_by_email_not_found(self):
        # GIVEN
        email = "nonexistent@example.com"
        self.mock_cursor.fetchone.return_value = None
        dao = UserDao()

        # WHEN
        result = dao.find_by_email(email)

        # THEN
        assert result is None

    def test_find_by_email_database_error(self):
        # GIVEN
        email = "test@example.com"
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = UserDao()

        # WHEN
        result = dao.find_by_email(email)

        # THEN
        assert result is None

    def test_list_all_success(self):
        # GIVEN
        mock_rows = [
            {
                "id": 1,
                "email": "user1@example.com",
                "password_hash": "hash1",
                "first_name": "John",
                "last_name": "Doe",
                "user_type": "student",
                "is_active": True,
                "created_at": datetime(2024, 1, 1, 10, 0, 0),
                "updated_at": datetime(2024, 1, 1, 10, 0, 0),
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "password_hash": "hash2",
                "first_name": "Jane",
                "last_name": "Smith",
                "user_type": "teacher",
                "is_active": True,
                "created_at": datetime(2024, 1, 1, 11, 0, 0),
                "updated_at": datetime(2024, 1, 1, 11, 0, 0),
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        with patch("dao.user_dao.create_user_from_type") as mock_create_user:
            mock_create_user.side_effect = [
                User(
                    id=1,
                    email="user1@example.com",
                    password_hash="hash1",
                    first_name="John",
                    last_name="Doe",
                    user_type="student",
                    is_active=True,
                ),
                User(
                    id=2,
                    email="user2@example.com",
                    password_hash="hash2",
                    first_name="Jane",
                    last_name="Smith",
                    user_type="teacher",
                    is_active=True,
                ),
            ]
            dao = UserDao()

            # WHEN
            result = dao.list_all()

            # THEN
            assert len(result) == 2
            assert all(isinstance(user, User) for user in result)
            assert mock_create_user.call_count == 2

    def test_list_all_empty(self):
        # GIVEN
        self.mock_cursor.fetchall.return_value = []
        dao = UserDao()

        # WHEN
        result = dao.list_all()

        # THEN
        assert result == []

    def test_list_all_database_error(self):
        # GIVEN
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = UserDao()

        # WHEN
        result = dao.list_all()

        # THEN
        assert result == []

    def test_delete_success(self):
        # GIVEN
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            user_type="student",
            is_active=True,
        )
        self.mock_cursor.rowcount = 1
        dao = UserDao()

        # WHEN
        result = dao.delete(user)

        # THEN
        assert result is True
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_delete_not_found(self):
        # GIVEN
        user = User(
            id=999,
            email="nonexistent@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            user_type="student",
            is_active=True,
        )
        self.mock_cursor.rowcount = 0
        dao = UserDao()

        # WHEN
        result = dao.delete(user)

        # THEN
        assert result is False
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_delete_database_error(self):
        # GIVEN
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            user_type="student",
            is_active=True,
        )
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = UserDao()

        # WHEN
        result = dao.delete(user)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()

    def test_update_success(self):
        # GIVEN
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Updated",
            last_name="Name",
            user_type="student",
            is_active=False,
        )
        dao = UserDao()

        # WHEN
        result = dao.update(user)

        # THEN
        assert result is True
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_update_database_error(self):
        # GIVEN
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Updated",
            last_name="Name",
            user_type="student",
            is_active=False,
        )
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = UserDao()

        # WHEN
        result = dao.update(user)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()
