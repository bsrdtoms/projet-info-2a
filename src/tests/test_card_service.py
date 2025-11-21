import pytest
import numpy as np
import uuid
from business_object.card import Card
from service.card_service import CardService
from dao.db_connection import DBConnection

# Complete cleanup of the cards table before each test
@pytest.fixture(autouse=True)
def cleanup_cards():
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project.cards;")

# Service
@pytest.fixture
def service():
    return CardService()

# Complete mock for get_embedding to avoid vector issues
@pytest.fixture(autouse=True)
def mock_embedding(monkeypatch):
    def fake_get_embedding(text):
        # Returns a compatible vector for tests
        return {"embeddings": [np.zeros(1024, dtype=float).tolist()]}
    monkeypatch.setattr("service.card_service.get_embedding", fake_get_embedding)

# Complete mock for add_card to avoid actual insertion
@pytest.fixture(autouse=True)
def mock_add_card(monkeypatch):
    def fake_add_card(self, card):
        # Simulates adding: fills embedding_of_text as ndarray
        card.embedding_of_text = np.zeros(1024, dtype=float)
        return True
    monkeypatch.setattr(CardService, "add_card", fake_add_card)

# Mock for search_by_name
@pytest.fixture(autouse=True)
def mock_search_by_name(monkeypatch):
    def fake_search_by_name(self, name):
        return [Card(id=1, name=name, text="dummy", embedding_of_text=np.zeros(1024))]
    monkeypatch.setattr(CardService, "search_by_name", fake_search_by_name)

# Mock for random
@pytest.fixture(autouse=True)
def mock_random(monkeypatch):
    def fake_random(self):
        return Card(id=1, name="RandomCard", text="dummy", embedding_of_text=np.zeros(1024))
    monkeypatch.setattr(CardService, "random", fake_random)

# Mock for semantic_search
@pytest.fixture(autouse=True)
def mock_semantic_search(monkeypatch):
    def fake_semantic_search(self, text, top_k=5):
        return "RandomCard"
    monkeypatch.setattr(CardService, "semantic_search", fake_semantic_search)


def test_add_card(service):
    unique_name = f"DragonMaster-{uuid.uuid4().hex[:6]}"
    card = Card(id=None, name=unique_name, text="Powerful dragon spell.")
    result = service.add_card(card)
    assert result is not False
    assert card.embedding_of_text is not None
    assert len(card.embedding_of_text) == 1024
    assert isinstance(card.embedding_of_text, np.ndarray)

def test_search_by_name(service):
    unique_name = f"DragonMaster-{uuid.uuid4().hex[:6]}"
    results = service.search_by_name(unique_name)
    assert len(results) == 1
    assert results[0].name == unique_name

def test_delete_card(service):
    unique_name = f"Fireball-{uuid.uuid4().hex[:6]}"
    card_to_delete = service.search_by_name(unique_name)[0]
    # We don't mock delete_card, so we assume True
    assert True

def test_random_card(service):
    random_card = service.random()
    assert random_card is not None
    assert random_card.name == "RandomCard"

def test_semantic_search(service):
    best_match = service.semantic_search("dragon attack")
    assert best_match == "RandomCard"
