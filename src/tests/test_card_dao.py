import pytest
from dao.card_dao import CardDao
from business_object.card import Card

@pytest.fixture
def dao():
    return CardDao()

@pytest.fixture
def sample_card():
    # Passer id=None pour que la DB l'assigne automatiquement
    return Card(
        id=None,
        name="Test Card",
        text="This is a test card",
        embedding_of_text=None
    )

def test_create_and_find_by_id(dao, sample_card):
    success = dao.create(sample_card)
    assert success, "La création de la carte a échoué"

    all_cards = dao.list_all()
    card_id = all_cards[-1].id
    card = dao.find_by_id(card_id)

    assert card is not None
    assert card.name == sample_card.name
    assert card.text == sample_card.text

def test_modify_card(dao, sample_card):
    dao.create(sample_card)
    card_id = dao.list_all()[-1].id
    card = dao.find_by_id(card_id)

    updates = {"name": "Updated Card", "text": "Updated text"}
    success = dao.modify_card(card, updates)
    assert success, "La modification a échoué"

    updated_card = dao.find_by_id(card_id)
    assert updated_card.name == "Updated Card"
    assert updated_card.text == "Updated text"

def test_delete_card(dao, sample_card):
    dao.create(sample_card)
    card_id = dao.list_all()[-1].id
    card = dao.find_by_id(card_id)

    success = dao.delete(card)
    assert success, "La suppression a échoué"

    deleted_card = dao.find_by_id(card_id)
    assert deleted_card is None

def test_search_by_name(dao, sample_card):
    dao.create(sample_card)
    results = dao.search_by_name("Test")
    assert any(c.name == sample_card.name for c in results)
