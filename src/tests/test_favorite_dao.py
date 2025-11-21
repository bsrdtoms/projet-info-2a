import pytest
from unittest.mock import Mock, patch, MagicMock

from dao.favorite_dao import FavoriteDAO
from business_object.card import Card


class TestFavoriteDAO:
    """Unit tests for the FavoriteDAO class"""
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Setup mocks to isolate tests from the database"""
        with patch('dao.favorite_dao.DBConnection') as mock_db_connection:
            self.mock_connection = MagicMock()
            self.mock_cursor = MagicMock()

            # Configure the connection mock
            self.mock_connection.__enter__ = Mock(return_value=self.mock_connection)
            self.mock_connection.__exit__ = Mock(return_value=None)
            self.mock_connection.cursor.return_value.__enter__ = Mock(return_value=self.mock_cursor)
            self.mock_connection.cursor.return_value.__exit__ = Mock(return_value=None)

            mock_db_connection.return_value.connection = self.mock_connection
            yield


    def test_add_favorite_success(self):
        """Test successful favorite addition (new entry)"""
        # GIVEN
        user_id = 1
        card_id = 123
        self.mock_cursor.rowcount = 1
        dao = FavoriteDAO()

        # WHEN
        result = dao.add_favorite(user_id, card_id)

        # THEN
        assert result is True
        self.mock_cursor.execute.assert_called_once()
        call_args = self.mock_cursor.execute.call_args[0]
        assert "INSERT INTO project.favorites" in call_args[0]
        assert call_args[1] == (1, 123)
        self.mock_connection.commit.assert_called_once()

    def test_add_favorite_already_exists(self):
        """Test adding favorite that already exists"""
        # GIVEN
        user_id = 1
        card_id = 123
        self.mock_cursor.rowcount = 0
        dao = FavoriteDAO()

        # WHEN
        result = dao.add_favorite(user_id, card_id)

        # THEN
        assert result is False
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_add_favorite_database_error(self):
        """Test adding favorite with database error"""
        # GIVEN
        user_id = 1
        card_id = 123
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = FavoriteDAO()

        # WHEN
        result = dao.add_favorite(user_id, card_id)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()


    def test_remove_favorite_success(self):
        """Test successful favorite removal"""
        # GIVEN
        user_id = 1
        card_id = 123
        self.mock_cursor.rowcount = 1
        dao = FavoriteDAO()

        # WHEN
        result = dao.remove_favorite(user_id, card_id)

        # THEN
        assert result is True
        self.mock_cursor.execute.assert_called_once()
        call_args = self.mock_cursor.execute.call_args[0]
        assert "DELETE FROM project.favorites" in call_args[0]
        assert call_args[1] == (1, 123)
        self.mock_connection.commit.assert_called_once()

    def test_remove_favorite_not_found(self):
        """Test removing favorite not found"""
        # GIVEN
        user_id = 1
        card_id = 999
        self.mock_cursor.rowcount = 0
        dao = FavoriteDAO()

        # WHEN
        result = dao.remove_favorite(user_id, card_id)

        # THEN
        assert result is False
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_remove_favorite_database_error(self):
        """Test removing favorite with database error"""
        # GIVEN
        user_id = 1
        card_id = 123
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = FavoriteDAO()

        # WHEN
        result = dao.remove_favorite(user_id, card_id)

        # THEN
        assert result is False
        self.mock_connection.commit.assert_not_called()

    # Tests for the list_favorites() method

    def test_list_favorites_success(self):
        """Test successful favorites list retrieval"""
        # GIVEN
        user_id = 1
        mock_rows = [
            {
                "card_id": 123,
                "id": 123,
                "name": "Test Card 1",
                "text": "Card 1 text",
                "embedding_of_text": [0.1, 0.2, 0.3]
            },
            {
                "card_id": 124,
                "id": 124,
                "name": "Test Card 2",
                "text": "Card 2 text",
                "embedding_of_text": [0.4, 0.5, 0.6]
            }
        ]
        self.mock_cursor.fetchall.return_value = mock_rows
        dao = FavoriteDAO()

        # WHEN
        result = dao.list_favorites(user_id)

        # THEN
        assert len(result) == 2
        assert isinstance(result[0], Card)
        assert result[0].id == 123
        assert result[0].name == "Test Card 1"
        assert result[1].id == 124
        assert result[1].name == "Test Card 2"

        self.mock_cursor.execute.assert_called_once()
        call_args = self.mock_cursor.execute.call_args[0]
        assert call_args[1] == (1,)

    def test_list_favorites_empty(self):
        """Test retrieving empty favorites list"""
        # GIVEN
        user_id = 999
        self.mock_cursor.fetchall.return_value = []
        dao = FavoriteDAO()

        # WHEN
        result = dao.list_favorites(user_id)

        # THEN
        assert result == []
        self.mock_cursor.execute.assert_called_once()

    def test_list_favorites_database_error(self):
        """Test retrieving favorites list with database error"""
        # GIVEN
        user_id = 1
        self.mock_cursor.execute.side_effect = Exception("DB error")
        dao = FavoriteDAO()

        # WHEN/THEN
        with pytest.raises(Exception, match="DB error"):
            dao.list_favorites(user_id)

    # Tests simples pour les cas limites

    def test_add_favorite_min_ids(self):
        """Test adding favorite with minimal IDs"""
        # GIVEN
        user_id = 1
        card_id = 1
        self.mock_cursor.rowcount = 1
        dao = FavoriteDAO()

        # WHEN
        result = dao.add_favorite(user_id, card_id)

        # THEN
        assert result is True
        call_args = self.mock_cursor.execute.call_args[0]
        assert call_args[1] == (1, 1)

    def test_add_favorite_max_ids(self):
        """Test adding favorite with high IDs"""
        # GIVEN
        user_id = 999999
        card_id = 999999
        self.mock_cursor.rowcount = 1
        dao = FavoriteDAO()

        # WHEN
        result = dao.add_favorite(user_id, card_id)

        # THEN
        assert result is True
        call_args = self.mock_cursor.execute.call_args[0]
        assert call_args[1] == (999999, 999999)

    def test_remove_favorite_min_ids(self):
        """Test removing favorite with minimal IDs"""
        # GIVEN
        user_id = 1
        card_id = 1
        self.mock_cursor.rowcount = 1
        dao = FavoriteDAO()

        # WHEN
        result = dao.remove_favorite(user_id, card_id)

        # THEN
        assert result is True
        call_args = self.mock_cursor.execute.call_args[0]
        assert call_args[1] == (1, 1)

    def test_remove_favorite_max_ids(self):
        """Test removing favorite with high IDs"""
        # GIVEN
        user_id = 999999
        card_id = 999999
        self.mock_cursor.rowcount = 1
        dao = FavoriteDAO()

        # WHEN
        result = dao.remove_favorite(user_id, card_id)

        # THEN
        assert result is True
        call_args = self.mock_cursor.execute.call_args[0]
        assert call_args[1] == (999999, 999999)
