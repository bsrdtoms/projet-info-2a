# tests/test_historical_search_bo.py
import pytest
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from business_object.historical_search import HistoricalSearch

class TestHistoricalSearch:

    def test_historical_search_init_basic(self):
        # GIVEN
        user_id = 42
        query_text = "pokemon cards"
        result_count = 5

        # WHEN
        search = HistoricalSearch(
            id=1,
            user_id=user_id,
            query_text=query_text,
            query_embedding=[0.1, 0.2, 0.3],
            result_count=result_count
        )

        # THEN
        assert search.id == 1
        assert search.user_id == user_id
        assert search.query_text == query_text
        assert search.query_embedding == [0.1, 0.2, 0.3]
        assert search.result_count == result_count
        assert isinstance(search.created_at, datetime)
        assert str(search).startswith("Search #1:")
        assert f"{result_count} results" in str(search)
        assert repr(search).startswith("HistoricalSearch(")
        assert f"user_id={user_id}" in repr(search)
        assert "query='pokemon cards" in repr(search)

    def test_historical_search_with_minimal_params(self):
        # GIVEN minimal initialization
        user_id = 7
        query_text = "test"

        # WHEN
        search = HistoricalSearch(user_id=user_id, query_text=query_text)

        # THEN
        assert search.id is None
        assert search.user_id == user_id
        assert search.query_text == query_text
        assert search.query_embedding is None
        assert search.result_count == 0
        assert isinstance(search.created_at, datetime)
        assert str(search).startswith("Search #None:")
        assert "0 results" in str(search)

    def test_custom_created_timestamp(self):
        # GIVEN
        user_id = 3
        query_text = "cards"
        created = datetime(2022, 1, 1, 12, 0)

        # WHEN
        search = HistoricalSearch(user_id=user_id, query_text=query_text, created_at=created)

        # THEN
        assert search.created_at == created
        assert search.user_id == user_id
        assert search.query_text == query_text
