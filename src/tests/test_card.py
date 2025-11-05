from src.business_object.card import Card


def test_card_basic():
    # Carte sans embedding
    card1 = Card(id=None, name="Fireball", text="Inflige 3 points de dégâts.")
    assert card1.id is None
    assert card1.name == "Fireball"
    assert card1.text == "Inflige 3 points de dégâts."
    assert card1.embedding_of_text is None

    # Test de la méthode __str__
    assert str(card1) == (
        "Carte (non enregistrée)\nNom : Fireball\nTexte : Inflige 3 points de dégâts."
    )

    # Test de la méthode __repr__
    assert repr(card1) == (
        "Card(id=None, name='Fireball', text='Inflige 3 points de dégâts.', embedding=No)"
    )

    # Carte avec embedding
    card2 = Card(
        id=42,
        name="DragonMaster",
        text="Puissant sort de dragon.",
        embedding_of_text=[0.1, 0.2],
    )
    assert card2.id == 42
    assert card2.name == "DragonMaster"
    assert card2.text == "Puissant sort de dragon."
    assert card2.embedding_of_text == [0.1, 0.2]

    # Test de la méthode __str__
    assert str(card2) == (
        "Carte 42\nNom : DragonMaster\nTexte : Puissant sort de dragon."
    )

    # Test de la méthode __repr__
    assert repr(card2) == (
        "Card(id=42, name='DragonMaster', text='Puissant sort de dragon.', embedding=Yes)"
    )


if __name__ == "__main__":
    test_card_basic()
    print("Tous les tests passent !")
