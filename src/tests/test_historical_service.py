import pytest
from unittest.mock import MagicMock, patch

# ----- MOCKS -----
class HistoricalSearch:
    def __init__(self, user_id, query_text, query_embedding, result_count):
        self.user_id = user_id
        self.query_text = query_text
        self.query_embedding = query_embedding
        self.result_count = result_count

class HistoricalSearchDAO:
    def add(self, search):
        return True
    def read_history(self, user_id, limit):
        return [HistoricalSearch(user_id, "query1", None, 5)]
    def delete_search(self, search_id):
        return True
    def clear_user_history(self, user_id):
        return True
    def get_user_search_stats(self, user_id):
        return {"total_searches": 3}

class HistoricalSearchService:
    def __init__(self):
        self.dao = HistoricalSearchDAO()
    
    def add_search(self, user_id, query_text, result_count, save_embedding=True):
        query_embedding = "mocked_embedding" if save_embedding and query_text else None
        historical_search = HistoricalSearch(user_id, query_text, query_embedding, result_count)
        return self.dao.add(historical_search)

    def get_history(self, user_id, limit=50):
        return self.dao.read_history(user_id, limit)

    def delete_search(self, search_id):
        return self.dao.delete_search(search_id)

    def clear_history(self, user_id):
        return self.dao.clear_user_history(user_id)

    def get_stats(self, user_id):
        return self.dao.get_user_search_stats(user_id)

# ----- FIXTURE -----
@pytest.fixture
def historical_service():
    service = HistoricalSearchService()
    service.dao = MagicMock(spec=HistoricalSearchDAO)

    # Valeurs de retour mockées
    service.dao.add.return_value = True
    service.dao.read_history.return_value = [HistoricalSearch(1, "query1", None, 5)]
    service.dao.delete_search.return_value = True
    service.dao.clear_user_history.return_value = True
    service.dao.get_user_search_stats.return_value = {"total_searches": 3}

    return service

# ----- TESTS UNITAIRES -----
def test_add_search(historical_service):
    # GIVEN
    user_id = 1
    query_text = "test query"
    result_count = 5

    # WHEN
    result = historical_service.add_search(user_id, query_text, result_count)

    # THEN
    historical_service.dao.add.assert_called_once()
    assert result is True

def test_get_history(historical_service):
    # GIVEN
    user_id = 1

    # WHEN
    history = historical_service.get_history(user_id)

    # THEN
    historical_service.dao.read_history.assert_called_once_with(user_id, 50)
    assert len(history) == 1
    assert history[0].query_text == "query1"

def test_delete_search(historical_service):
    # GIVEN
    search_id = 10

    # WHEN
    result = historical_service.delete_search(search_id)

    # THEN
    historical_service.dao.delete_search.assert_called_once_with(search_id)
    assert result is True

def test_clear_history(historical_service):
    # GIVEN
    user_id = 1

    # WHEN
    result = historical_service.clear_history(user_id)

    # THEN
    historical_service.dao.clear_user_history.assert_called_once_with(user_id)
    assert result is True

def test_get_stats(historical_service):
    # GIVEN
    user_id = 1

    # WHEN
    stats = historical_service.get_stats(user_id)

    # THEN
    historical_service.dao.get_user_search_stats.assert_called_once_with(user_id)
    assert stats["total_searches"] == 3
