from src.business_object.card import Card


def test_card_basic():
    # Card without embedding
    card1 = Card(id=None, name="Fireball", text="Deals 3 damage.")
    assert card1.id is None
    assert card1.name == "Fireball"
    assert card1.text == "Deals 3 damage."
    assert card1.embedding_of_text is None

    # Test of the __str__ method
    assert str(card1) == (
        "Card (not registered)\nName: Fireball\nText: Deals 3 damage."
    )

    # Test of the __repr__ method
    assert repr(card1) == (
        "Card(id=None, name='Fireball', text='Deals 3 damage.', embedding=No)"
    )

    # Card with embedding
    card2 = Card(
        id=42,
        name="DragonMaster",
        text="Powerful dragon spell.",
        embedding_of_text=[0.1, 0.2],
    )
    assert card2.id == 42
    assert card2.name == "DragonMaster"
    assert card2.text == "Powerful dragon spell."
    assert card2.embedding_of_text == [0.1, 0.2]

    # Test of the __str__ method
    assert str(card2) == (
        "Card 42\nName: DragonMaster\nText: Powerful dragon spell."
    )

    # Test of the __repr__ method
    assert repr(card2) == (
        "Card(id=42, name='DragonMaster', text='Powerful dragon spell.', embedding=Yes)"
    )


if __name__ == "__main__":
    test_card_basic()
    print("All tests pass!")
