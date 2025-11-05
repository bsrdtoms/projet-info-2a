from dao.db_connection import DBConnection
from service.card_service import CardService
from dao.card_dao import CardDao
from technical_components.embedding.ollama_embedding import get_embedding


def float_list_to_pg_array(floats):
    """
    Convert list of floats to PostgreSQL array literal. 
    """
    return "[" + ",".join(str(f) for f in floats) + "]"

def launch():
    cards = CardDao().list_all()

    if not cards:
        print("⚠️ No cards found in database.")
        return

    # Filtrer uniquement les cartes avec un texte
    cards_with_text = [card for card in cards if card.text is not None]

    if not cards_with_text:
        print("⚠️ No cards with text to process.")
        return

    list_of_texts = [card.text for card in cards_with_text]

    # pour que l'API get_embeddings n'ait pas à traiter trop de textes d'un coup, 
    # on découpe par lots de 10000.
    size_of_slice = 10000
    list_of_embeddings = []
    for i in range(0, len(list_of_texts), size_of_slice):
        print("carte", i)
        # Get embeddings from the API
        response = get_embedding(list_of_texts[i:i+size_of_slice])
        list_of_embeddings.extend(response['embeddings'])
    print("✅ End of embeddings generation.")

    # mise à jour
    for card, emb in zip(cards_with_text, list_of_embeddings):
        pg_array = float_list_to_pg_array(emb)
        success = CardDao().modify(card.id, "embedding_of_text", pg_array)
        if not success:
            print(f"⚠️ Failed to update card {card.id}")

    print(f"✅ Updated embeddings for {len(cards_with_text)} cards.")


launch()