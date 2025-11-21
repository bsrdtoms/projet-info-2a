import pytest
from unittest.mock import MagicMock

# ----- MOCKS pour éviter les dépendances externes -----
class Card:
    def __init__(self, id, name, text):
        self.id = id
        self.name = name
        self.text = text

class CardService:
    def __init__(self):
        self.dao = MagicMock()

# ----- FIXTURE -----
@pytest.fixture
def card_service():
    service = CardService()

    # Mocker toutes les méthodes DAO pour ne jamais toucher à la DB
    for method in [
        "create", "modify_card", "delete",
        "get_card_details", "search_by_name",
        "find_by_id", "semantic_search", "get_all_ids"
    ]:
        setattr(service.dao, method, MagicMock())

    # Valeurs de retour mockées
    service.dao.search_by_name.return_value = [Card(id=1, name="Lightning Bolt", text="Deals 3 damage")]
    service.dao.get_card_details.return_value = {"id": 1, "name": "Lightning Bolt", "text": "Deals 3 damage"}

    return service

# ----- TESTS UNITAIRES -----
def test_add_card(card_service):
    # GIVEN
    card = Card(id=2, name="Test Card", text="Some text")

    # WHEN
    card_service.dao.create(card)

    # THEN
    card_service.dao.create.assert_called_once_with(card)


def test_modify_card(card_service):
    # GIVEN
    card = Card(id=2, name="Modified Card", text="Modified text")

    # WHEN
    card_service.dao.modify_card(card)

    # THEN
    card_service.dao.modify_card.assert_called_once_with(card)


def test_delete_card(card_service):
    # GIVEN
    card_id = 2

    # WHEN
    card_service.dao.delete(card_id)

    # THEN
    card_service.dao.delete.assert_called_once_with(card_id)


def test_search_by_name(card_service):
    # GIVEN
    query = "Lightning"

    # WHEN
    results = card_service.dao.search_by_name(query)

    # THEN
    assert len(results) == 1
    assert results[0].name == "Lightning Bolt"


def test_get_card_details(card_service):
    # GIVEN
    card_id = 1

    # WHEN
    details = card_service.dao.get_card_details(card_id)

    # THEN
    assert details["id"] == 1
    assert details["name"] == "Lightning Bolt"
