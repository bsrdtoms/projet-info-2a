import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

mock_log = MagicMock()
mock_log.side_effect = lambda func: func

mocks = {
    "utils.log_decorator": MagicMock(),
    "dao.favorite_dao": MagicMock(),
}

mocks["utils.log_decorator"].log = mock_log

for module_name, mock in mocks.items():
    sys.modules[module_name] = mock

# Import de FavoriteService après le mock
from service.favorite_service import FavoriteService


@pytest.fixture
def service():
    service = FavoriteService()
    # Remplace la DAO par un mock
    service.dao = MagicMock()
    service.dao.add_favorite.return_value = True
    service.dao.remove_favorite.return_value = True
    service.dao.list_favorites.return_value = []
    return service


def test_add_favorite_success(service):
    service.dao.add_favorite.return_value = True
    success, msg = service.add_favorite(1, 101)
    assert success is True
    assert msg == "Carte ajoutée aux favoris"
    service.dao.add_favorite.assert_called_once_with(1, 101)


def test_add_favorite_already_exists(service):
    service.dao.add_favorite.return_value = False
    success, msg = service.add_favorite(1, 101)
    assert success is False
    assert msg == "La carte est déjà en favoris (ou échec d'ajout)"
    service.dao.add_favorite.assert_called_once_with(1, 101)


def test_remove_favorite_success(service):
    service.dao.remove_favorite.return_value = True
    success, msg = service.remove_favorite(1, 101)
    assert success is True
    assert msg == "Carte retirée des favoris"
    service.dao.remove_favorite.assert_called_once_with(1, 101)


def test_remove_favorite_not_found(service):
    service.dao.remove_favorite.return_value = False
    success, msg = service.remove_favorite(1, 999)
    assert success is False
    assert msg == "Carte non trouvée"
    service.dao.remove_favorite.assert_called_once_with(1, 999)


def test_list_favorites(service):
    service.dao.list_favorites.return_value = [101, 102]
    result = service.list_favorites(1)
    assert result == [101, 102]
    service.dao.list_favorites.assert_called_once_with(1)
