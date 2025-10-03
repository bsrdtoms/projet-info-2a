from dao.db_connection import DBConnection
from business_object.use_the_sspcloud_api import get_embedding


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
