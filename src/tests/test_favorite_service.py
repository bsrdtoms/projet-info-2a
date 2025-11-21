
import pytest
from unittest.mock import MagicMock, patch
import sys

mock_log = MagicMock()
mock_log.side_effect = lambda func: func  

mocks = {
    'utils.log_decorator': MagicMock(),
    'dao.db_connection': MagicMock(),
    'dao.favorite_dao': MagicMock(),
    'business_object.favorite': MagicMock(),
}

mocks['utils.log_decorator'].log = mock_log

for module_name, mock in mocks.items():
    sys.modules[module_name] = mock


from service.favorite_service import FavoriteService

@pytest.fixture
def service():
    service = FavoriteService()

    service.dao = MagicMock()
    service.dao.is_favorite.return_value = False
    service.dao.add_favorite.return_value = True
    service.dao.remove_favorite.return_value = True
    service.dao.list_favorites.return_value = []
    
    return service

def test_add_favorite_success(service):
    service.dao.is_favorite.return_value = False
    service.dao.add_favorite.return_value = True

    success, msg = service.add_favorite(1, 101)

    assert success is True
    assert msg == "Card added to favorites"
    service.dao.is_favorite.assert_called_once_with(1, 101)
    service.dao.add_favorite.assert_called_once_with(1, 101)

def test_add_favorite_already_exists(service):
    service.dao.is_favorite.return_value = True

    success, msg = service.add_favorite(1, 101)

    assert success is False
    assert msg == "Card is already in favorites"
    service.dao.is_favorite.assert_called_once_with(1, 101)
    service.dao.add_favorite.assert_not_called()

def test_remove_favorite_success(service):
    service.dao.remove_favorite.return_value = True

    success, msg = service.remove_favorite(1, 101)

    assert success is True
    assert msg == "Card removed from favorites"
    service.dao.remove_favorite.assert_called_once_with(1, 101)

def test_remove_favorite_not_found(service):
    service.dao.remove_favorite.return_value = False

    success, msg = service.remove_favorite(1, 999)

    assert success is False
    assert msg == "Card not found"
    service.dao.remove_favorite.assert_called_once_with(1, 999)

def test_list_favorites(service):
    service.dao.list_favorites.return_value = [101, 102]
    
    result = service.list_favorites(1)
    
    assert result == [101, 102]
    service.dao.list_favorites.assert_called_once_with(1)
