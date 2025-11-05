import pytest
from dao.card_dao import CardDao
from business_object.card import Card
from dao.db_connection import DBConnection

## IMPORTANT !!! le nettoyage 
@pytest.fixture(autouse=True)
def cleanup_before_tests():
    """Nettoie les cartes Fireball avant chaque test"""
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project.cards WHERE name = 'Fireball';")


# Initialisation de la classe CardDao
dao = CardDao()


@pytest.fixture(scope="module")
def setup_db():
    """Fixture pour préparer la base de données pour les tests"""
    # On peut créer une base de données de test ici si nécessaire.
    # Cette fixture va être exécutée avant tous les tests.
    print("Base de données de test prête")

    # Nettoyage de la base de données avant les tests
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project.cards")
    yield
    # Code de nettoyage si nécessaire après les tests
    print("Tests terminés, base de données nettoyée")


def test_create_card(setup_db):
    """Test de la méthode create"""
    card = Card(id=None, name="Fireball", text="Inflige 3 points de dégâts.")
    assert dao.create(card)  # Doit retourner True car l'insertion réussie


def test_search_by_name(setup_db):
    """Test de la méthode search_by_name"""
    # On commence par insérer une carte à rechercher
    card = Card(id=None, name="DragonMaster", text="Sort de dragon puissant.")
    dao.create(card)

    # Recherche de la carte insérée
    cards = dao.search_by_name("DragonMaster")
    assert len(cards) > 0  # Il doit y avoir au moins une carte correspondant à ce nom
    assert cards[0].name == "DragonMaster"
    assert cards[0].text == "Sort de dragon puissant."


def test_list_all_cards(setup_db):
    """Test de la méthode list_all"""
    # On insère plusieurs cartes pour tester la récupération de toutes les cartes
    card1 = Card(id=None, name="Fireball", text="Inflige 3 points de dégâts.")
    card2 = Card(id=None, name="DragonMaster", text="Sort de dragon puissant.")
    dao.create(card1)
    dao.create(card2)

    # Récupération de toutes les cartes
    cards = dao.list_all()
    assert len(cards) >= 2  # Il doit y avoir au moins 2 cartes
    assert any(card.name == "Fireball" for card in cards)
    assert any(card.name == "DragonMaster" for card in cards)


def test_delete_card(setup_db):
    """Test de la méthode delete"""
    # On crée d'abord une carte à supprimer
    card = Card(id=None, name="Fireball", text="Inflige 3 points de dégâts.")
    dao.create(card)

    # On récupère l'id de la carte pour la suppression
    card_to_delete = dao.search_by_name("Fireball")[0]

    # Suppression de la carte
    assert dao.delete(card_to_delete)  # La suppression doit réussir

    # On vérifie que la carte a bien été supprimée
    cards_after_deletion = dao.search_by_name("Fireball")
    assert len(cards_after_deletion) == 0  # La carte ne doit plus être trouvée
