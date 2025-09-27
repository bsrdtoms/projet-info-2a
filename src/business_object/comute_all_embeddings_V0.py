'''from dao.db_connection import DBConnection
import os
import requests
import json

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

    # Extract texts for embeddings
    list_of_texts = [row['text'] for row in rows]
    # Get embeddings from the API
    list_of_embeddings = get_embedding(list_of_texts[:270])
    # Update embeddings in the database
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                for idx, emb in enumerate(list_of_embeddings):
                    card_id = rows[idx]["id"]
                    # Convert Python list to PostgreSQL array literal
                    pg_array = "{" + ",".join(map(str, emb)) + "}"
                    update_sql = f"""
                        UPDATE project.cards
                        SET embedding_of_text = '{pg_array}'
                        WHERE id = {card_id};
                    """
                    embedding = list_of_embeddings["embeddings"][idx]  # assuming API returns {"embedding": [...]}
                    pg_array = float_list_to_pg_array(embedding)

                    update_sql = f"""
                    UPDATE project.cards
                    SET embedding_of_text = '{pg_array}'
                    WHERE id = {rows[idx]['id']};
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
