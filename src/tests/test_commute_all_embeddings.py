import pytest
from unittest.mock import patch
import importlib

class FakeCard:
    def __init__(self, id, text):
        self.id = id
        self.text = text


def test_launch_with_mocked_db_and_embeddings(monkeypatch):
    dummy_cards = [DummyCard(1, "texte1"), DummyCard(2, "texte2")]

    # On prépare les mocks AVANT d'importer le module
    with patch("dao.card_dao.CardDao") as MockCardDao, \
         patch("technical_components.embedding.ollama_embedding.get_embedding") as mock_get_embedding:
        
        instance = MockCardDao.return_value
        instance.list_all.return_value = dummy_cards
        instance.modify.return_value = True
        mock_get_embedding.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}

        # Import du module après le patch pour empêcher l'exécution réelle
        cae = importlib.import_module("technical_components.embedding.comute_all_embeddings")

        # Lancer la fonction manuellement pour tester son comportement
        cae.launch()

        # Vérifications
        instance.list_all.assert_called_once()
        assert instance.modify.call_count == len(dummy_cards)
        args_first_call = instance.modify.call_args_list[0][0]
        args_second_call = instance.modify.call_args_list[1][0]
        assert args_first_call[1] == "embedding_of_text"
        assert args_first_call[2] == "[0.1,0.2]"
        assert args_second_call[2] == "[0.3,0.4]"
