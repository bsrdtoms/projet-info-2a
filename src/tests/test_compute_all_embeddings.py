# tests/test_compute_all_embeddings.py

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.update({
    "POSTGRES_HOST": "localhost",
    "POSTGRES_DATABASE": "x",
    "POSTGRES_USER": "x",
    "POSTGRES_PASSWORD": "x",
    "POSTGRES_SCHEMA": "x",
    "POSTGRES_PORT": "5432"
})

class MockCard:
    def __init__(self, id, text):
        self.id = id
        self.text = text

with patch("psycopg2.connect") as mock_connect:
    mock_connect.return_value = MagicMock()
    from technical_components.embedding import compute_all_embeddings as cae

# Tests unitaires 
# -------------------------------

def test_launch_nominal():
    # GIVEN 
    cards = [MockCard(1, "texte1"), MockCard(2, "texte2")]

    with patch("technical_components.embedding.compute_all_embeddings.CardDao") as MockCardDao:
        instance = MockCardDao.return_value
        instance.list_all.return_value = cards

        with patch("technical_components.embedding.compute_all_embeddings.get_embedding") as mock_get:
            mock_get.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}

            # WHEN 
            cae.launch()

            # THEN 
            instance.list_all.assert_called_once()

def test_launch_no_cards():
    # GIVEN 
    with patch("technical_components.embedding.compute_all_embeddings.CardDao") as MockCardDao:
        instance = MockCardDao.return_value
        instance.list_all.return_value = []

        # WHEN 
        cae.launch()

        # THEN 
        instance.list_all.assert_called_once()

def test_launch_cards_without_text():
    # GIVEN 
    cards = [MockCard(1, None), MockCard(2, None)]

    with patch("technical_components.embedding.compute_all_embeddings.CardDao") as MockCardDao:
        instance = MockCardDao.return_value
        instance.list_all.return_value = cards

        # WHEN 
        cae.launch()

        # THEN 
        instance.list_all.assert_called_once()

def test_launch_bad_embedding_format():
    # GIVEN 
    cards = [MockCard(1, "texte1")]

    with patch("technical_components.embedding.compute_all_embeddings.CardDao") as MockCardDao:
        instance = MockCardDao.return_value
        instance.list_all.return_value = cards

        with patch("technical_components.embedding.compute_all_embeddings.get_embedding") as mock_get:
            mock_get.return_value = {"wrong_key": []} 
            with pytest.raises(KeyError):
                cae.launch()

def test_launch_modify_failure():
    # GIVEN 
    cards = [MockCard(1, "texte1")]

    with patch("technical_components.embedding.compute_all_embeddings.CardDao") as MockCardDao:
        instance = MockCardDao.return_value
        instance.list_all.return_value = cards
        instance.modify.side_effect = Exception("DB update failed")
        with pytest.raises(Exception):
            cae.launch()

def test_launch_batches_of_10000():
    # GIVEN 
    cards = [MockCard(i, f"texte{i}") for i in range(25000)]

    with patch("technical_components.embedding.compute_all_embeddings.CardDao") as MockCardDao:
        instance = MockCardDao.return_value
        instance.list_all.return_value = cards

        with patch("technical_components.embedding.compute_all_embeddings.get_embedding") as mock_get:
            mock_get.return_value = {"embeddings": [[0.1, 0.2]] * 10000}

            # WHEN 
            cae.launch()

            # THEN 
            instance.list_all.assert_called_once()
