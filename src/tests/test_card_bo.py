# tests/test_card_bo.py
import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from business_object.card import Card


class TestCard:

    def test_card_init_basic(self):
        # GIVEN
        card_id = 1
        name = "Black Lotus"
        text = "Add three mana of any one color."

        # WHEN
        card = Card(id=card_id, name=name, text=text, embedding_of_text=[0.1, 0.2, 0.3])

        # THEN
        assert card.id == card_id
        assert card.name == name
        assert card.text == text
        assert card.embedding_of_text == [0.1, 0.2, 0.3]

    def test_card_str_with_text(self):
        # GIVEN
        name = "Counterspell"
        text = "Counter target spell."
        card = Card(id=2, name=name, text=text)

        # WHEN
        string_repr = str(card)

        # THEN
        assert "Card 2" in string_repr
        assert name in string_repr
        assert text in string_repr
        assert card.is_truncated is False

    def test_card_str_truncated_text(self):
        # GIVEN
        name = "LongCard"
        text = "A" * 150  # texte > 100 caractères
        card = Card(id=3, name=name, text=text)

        # WHEN
        string_repr = str(card)

        # THEN
        assert string_repr.startswith("Card 3")
        assert card.is_truncated is True
        assert "..." in string_repr

    def test_card_str_no_id_no_text(self):
        # GIVEN
        name = "Mystery Card"
        card = Card(id=None, name=name, text=None)

        # WHEN
        string_repr = str(card)

        # THEN
        assert "(not saved)" in string_repr
        assert name in string_repr
        assert card.is_truncated is False

    def test_card_repr_method(self):
        # GIVEN
        name = "Lightning Bolt"
        text = "Deal 3 damage to any target."
        card = Card(id=4, name=name, text=text)

        # WHEN
        repr_str = repr(card)

        # THEN
        assert repr_str.startswith("Card(")
        assert name in repr_str
        assert text in repr_str
