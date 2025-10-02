from dao.db_connection import DBConnection
import os
import requests


def get_embedding(texts):
    """Call the embedding API and return a list of embeddings."""
    token = os.getenv("API_TOKEN")
    url = "https://llm.lab.sspcloud.fr/ollama/api/embed"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "bge-m3:latest",
        "input": texts
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()  # assume it returns a list of embeddings


def float_list_to_pg_array(floats):
    # Convert list of floats to PostgreSQL array literal
    return "{" + ",".join(str(f) for f in floats) + "}"


def launch():
    sql_query = "SELECT id, text FROM project.cards"

    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()  # rows = [(id, text), ...]
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise

    if not rows:
        print("⚠️ No cards found in database.")
        return
    print(type(rows[0]))
    cleaned_dict_of_texts = [row for row in rows if row.get("text") is not None]

    # Extract texts for embeddings
    list_of_index = []
    list_of_texts = []
    for d in cleaned_dict_of_texts:
        list_of_index.append(d['id'])
        list_of_texts.append(d['text'])

    size_of_slice = 10000

    list_of_embeddings = []
    for i in range(0, len(list_of_texts), size_of_slice):
        print("carte", i)
        # Get embeddings from the API
        list_of_embeddings.extend(get_embedding(list_of_texts[i:i+size_of_slice])['embeddings'])
    print("end of embeddings")

    # print(list_of_texts[270])
    # Update embeddings in the database
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                for i in range(len(list_of_embeddings)):
                    card_id = list_of_index[i]
                    emb = list_of_embeddings[i]
                    # Convert Python list to PostgreSQL array literal
                    pg_array = float_list_to_pg_array(emb)
                    update_sql = f"""
                        UPDATE project.cards
                        SET embedding_of_text = '{pg_array}'
                        WHERE id = {card_id};
                    """

                    cursor.execute(update_sql)
            connection.commit()
        print(f"✅ Updated embeddings for {len(rows)} cards.")
    except Exception as e:
        print(f"❌ SQL Error: {e}")
        raise


if __name__ == "__main__":
    launch()
'''

from dao.db_connection import DBConnection
import os
import requests
import json

BATCH_SIZE = 200

def get_embedding(texts):
    """Call the embedding API and return a list of embeddings."""
    token = os.getenv("API_TOKEN")
    url = "https://llm.lab.sspcloud.fr/ollama/api/embed"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "bge-m3:latest",
        "input": texts
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()  # assume it returns a list of embeddings


def float_list_to_pg_array(floats):
    """Convert list of floats to PostgreSQL array literal."""
    return "{" + ",".join(str(f) for f in floats) + "}"


def launch():
    # 1. Fetch all card IDs and texts
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, text FROM project.cards")
                rows = cursor.fetchall()  # list of dicts if using RealDictCursor
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise

    if not rows:
        print("⚠️ No cards found in database.")
        return

    # 2. Process in batches
    total_cards = len(rows)
    print(f"📊 Found {total_cards} cards. Processing in batches of {BATCH_SIZE}...")

    for start_idx in range(0, total_cards, BATCH_SIZE):
        end_idx = min(start_idx + BATCH_SIZE, total_cards)
        batch_rows = rows[start_idx:end_idx]
        batch_texts = [row["text"] for row in batch_rows]

        print(f"🔹 Processing batch {start_idx} to {end_idx-1}...")

        try:
            embeddings_response = get_embedding(batch_texts)
            # Assuming API returns a list of dicts: [{"embedding": [...]}, ...]
            embeddings = [item["embedding"] for item in embeddings_response]
        except Exception as e:
            print(f"❌ Error getting embeddings for batch {start_idx}-{end_idx-1}: {e}")
            continue

        # 3. Update embeddings in DB
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    for row, emb in zip(batch_rows, embeddings):
                        pg_array = float_list_to_pg_array(emb)
                        update_sql = f"""
                            UPDATE project.cards
                            SET embedding_of_text = '{pg_array}'
                            WHERE id = {row['id']};
                        """
                        cursor.execute(update_sql)
                connection.commit()
            print(f"✅ Updated embeddings for batch {start_idx}-{end_idx-1}.")
        except Exception as e:
            print(f"❌ SQL Error for batch {start_idx}-{end_idx-1}: {e}")
            continue

    print("🎉 All embeddings updated.")


if __name__ == "__main__":
    launch()
'''
