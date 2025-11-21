import os
import importlib
from unittest.mock import patch, MagicMock

def test_launch_nominal():
    class MockCard:
        def __init__(self, card_id, text):
            self.id = card_id
            self.text = text

    mock_cards = [MockCard(1, "Text 1"), MockCard(2, "Text 2")]
    with patch.dict(os.environ, {
        "POSTGRES_HOST": "x",
        "POSTGRES_PORT": "5432",  
        "POSTGRES_DATABASE": "x",
        "POSTGRES_USER": "x",
        "POSTGRES_PASSWORD": "x",
        "POSTGRES_SCHEMA": "x"
    }), patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with patch("technical_components.embedding.compute_all_embeddings.CardDao") as mock_card_dao, \
             patch("technical_components.embedding.compute_all_embeddings.get_embedding") as mock_get_embedding, \
             patch("technical_components.embedding.compute_all_embeddings.float_list_to_pg_array") as mock_converter, \
             patch("builtins.print") as mock_print:

            mock_dao_instance = MagicMock()
            mock_dao_instance.list_all.return_value = mock_cards
            mock_dao_instance.modify.return_value = True
            mock_card_dao.return_value = mock_dao_instance

            mock_get_embedding.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
            mock_converter.side_effect = lambda x: f"[{','.join(str(f) for f in x)}]"


            cae = importlib.import_module("technical_components.embedding.compute_all_embeddings")
            cae.launch()


            mock_dao_instance.list_all.assert_called_once()
            mock_get_embedding.assert_called_once_with(["Text 1", "Text 2"])
            assert mock_dao_instance.modify.call_count == 2
            mock_print.assert_any_call("✅ Updated embeddings for 2 cards.")
