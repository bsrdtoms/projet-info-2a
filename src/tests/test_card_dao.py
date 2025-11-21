import pytest
from dao.card_dao import CardDao
from business_object.card import Card
from dao.db_connection import DBConnection


## IMPORTANT!!! cleanup
@pytest.fixture(autouse=True)
def cleanup_before_tests():
    """Cleans Fireball cards before each test"""
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project.cards WHERE name = 'Fireball';")


# Initialize the CardDao class
dao = CardDao()


@pytest.fixture(scope="module")
def setup_db():
    """Fixture to prepare the database for tests"""
    # We can create a test database here if needed.
    # This fixture will be executed before all tests.
    print("Test database ready")

    # Clean the database before tests
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project.cards")
    yield
    # Cleanup code if needed after tests
    print("Tests completed, database cleaned")


def test_create_card(setup_db):
    """Test of the create method"""
    card = Card(id=None, name="Fireball", text="Deals 3 damage.")
    assert dao.create(card)  # Should return True because insertion succeeded


def test_search_by_name(setup_db):
    """Test of the search_by_name method"""
    # First insert a card to search for
    card = Card(id=None, name="DragonMaster", text="Powerful dragon spell.")
    dao.create(card)

    # Search for the inserted card
    cards = dao.search_by_name("DragonMaster")
    assert len(cards) > 0  # There should be at least one card matching this name
    assert cards[0].name == "DragonMaster"
    assert cards[0].text == "Powerful dragon spell."


def test_list_all_cards(setup_db):
    """Test of the list_all method"""
    # Insert multiple cards to test retrieving all cards
    card1 = Card(id=None, name="Fireball", text="Deals 3 damage.")
    card2 = Card(id=None, name="DragonMaster", text="Powerful dragon spell.")
    dao.create(card1)
    dao.create(card2)

    # Retrieve all cards
    cards = dao.list_all()
    assert len(cards) >= 2  # There should be at least 2 cards
    assert any(card.name == "Fireball" for card in cards)
    assert any(card.name == "DragonMaster" for card in cards)


def test_delete_card(setup_db):
    """Test of the delete method"""
    # First create a card to delete
    card = Card(id=None, name="Fireball", text="Deals 3 damage.")
    dao.create(card)

    # Get the card's ID for deletion
    card_to_delete = dao.search_by_name("Fireball")[0]

    # Delete the card
    assert dao.delete(card_to_delete)  # Deletion should succeed

    # Verify the card has been deleted
    cards_after_deletion = dao.search_by_name("Fireball")
    assert len(cards_after_deletion) == 0  # The card should no longer be found
