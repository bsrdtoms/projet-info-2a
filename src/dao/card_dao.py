"""
DAO for Magic cards with pgvector support
"""

from dao.db_connection import DBConnection
from business_object.card import Card
from utils.log_decorator import log


class CardDao:
    """Class containing methods to access Cards in the database"""

    @log
    def create(self, card: Card) -> bool:
        """
        Create a card in the database

        Parameters
        ----------
        card : Card
            Card object to insert

        Returns
        -------
        bool
            True if creation is successful, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # ID is not inserted as it's usually AUTO_INCREMENT
                    # embedding_of_text can be None
                    cursor.execute(
                        """
                        INSERT INTO project.cards (name, text, embedding_of_text)
                        VALUES (%s, %s, %s)
                        """,
                        (card.name, card.text, card.embedding_of_text),
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error during insertion: {e}")
            return False

    @log
    def delete(self, card: Card) -> bool:
        """
        Delete a card from the database

        Parameters
        ----------
        card : Card
            Card object to delete

        Returns
        -------
        bool
            True if deletion is successful, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM project.cards
                        WHERE id = %s
                        """,
                        (card.id,),
                    )
                    # Check that a row was actually deleted
                    if cursor.rowcount == 0:
                        print(f"❌ No card found with id {card.id} ({card.name})")
                        return False
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error during deletion: {e}")
            return False

    @log
    def modify_card(self, card: Card, updates: dict) -> bool:
        """
        Update specified columns of a given card

        Parameters
        ----------
        card : Card
            Card to modify
        updates : dict
            Dictionary {column: new_value} of fields to update

        Returns
        -------
        bool
            True if modification is successful, False otherwise
        """
        if not updates:
            print("❌ No updates provided")
            return False

        cols = []
        values = []
        for col, val in updates.items():
            cols.append(f"{col} = %s")
            values.append(val)

        set_clause = ", ".join(cols)
        values.append(card.id)

        query = f"""
            UPDATE project.cards
            SET {set_clause}
            WHERE id = %s
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, values)
                    if cursor.rowcount == 0:
                        print(f"❌ No record found with id {card.id}")
                        return False
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error during modification: {e}")
            return False

    @log
    def get_card_details(self, card_id: int) -> dict:
        """
        Get detailed information about a card for description generation

        Parameters
        ----------
        card_id : int
            Card ID

        Returns
        -------
        dict or None
            Dictionary with card details (name, type, mana_cost, text, colors, 
            power, toughness, etc.) or None if card not found
        """
        sql_query = """
            SELECT 
                id, name, type, mana_cost, text, 
                colors, power, toughness, loyalty,
                types, subtypes, supertypes
            FROM project.cards
            WHERE id = %s
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, (card_id,))
                    row = cursor.fetchone()

                    if not row:
                        print(f"❌ No card found with id {card_id}")
                        return None

                    return {
                        'id': row['id'],
                        'name': row['name'],
                        'type': row['type'],
                        'mana_cost': row['mana_cost'],
                        'text': row['text'],
                        'colors': row['colors'],
                        'power': row['power'],
                        'toughness': row['toughness'],
                        'loyalty': row['loyalty'],
                        'types': row['types'],
                        'subtypes': row['subtypes'],
                        'supertypes': row['supertypes']
                    }

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

    @log
    def find_by_id(self, card_id: int) -> Card:
        """
        Find a card by its ID

        Parameters
        ----------
        card_id : int
            ID of the card to find

        Returns
        -------
        Card
            Card object corresponding to the ID
        
        Raises
        ------
        Exception
            If database error occurs
        """
        sql_query = """
            SELECT id, name, text, embedding_of_text
            FROM project.cards
            WHERE id = %s
        """
     
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, (card_id,))
                    row = cursor.fetchone()

                    if not row:
                        print(f"❌ No card found with id {card_id}")
                        return None

                    card = Card(
                        id=row["id"],
                        name=row["name"],
                        text=row["text"],
                        embedding_of_text=row["embedding_of_text"],
                    )
                    return card

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

    @log
    def search_by_name(self, name: str) -> list[Card]:
        """
        Search for cards whose name contains the given text (case insensitive)

        Parameters
        ----------
        name : str
            Name (or partial name) of the card to search for

        Returns
        -------
        list[Card]
            List of Card objects matching the search criteria
        
        Raises
        ------
        Exception
            If database error occurs
        """
        sql_query = """
            SELECT id, name, text, embedding_of_text
            FROM project.cards
            WHERE LOWER(name) LIKE LOWER(%s)
        """
        cards = []

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, (f"%{name}%",))
                    rows = cursor.fetchall()

                    for row in rows:
                        card = Card(
                            id=row["id"],
                            name=row["name"],
                            text=row["text"],
                            embedding_of_text=row["embedding_of_text"],
                        )
                        cards.append(card)

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

        return cards

    @log
    def semantic_search(
        self, 
        query_embedding: list[float], 
        top_k: int = 5, 
        distance: str = "L2"
    ) -> list[tuple[Card, float]]:
        """
        Semantic search using pgvector (optimized)

        Parameters
        ----------
        query_embedding : list[float]
            Embedding of the search text
        top_k : int, optional
            Number of results to return (default: 5)
        distance : str, optional
            Distance metric to use: "L2" or "cosine" (default: "L2")

        Returns
        -------
        list[tuple[Card, float]]
            List of tuples (Card, similarity_score)
        
        Raises
        ------
        Exception
            If database error occurs or invalid distance metric
        """
        # Convert embedding to pgvector format
        embedding_str = "[" + ",".join(str(f) for f in query_embedding) + "]"

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Use pgvector operators
                    # Smaller distance = more similar
                    if distance == "L2":
                        # <-> is L2 distance operator
                        cursor.execute(
                            """
                            SELECT
                                id,
                                name,
                                text,
                                1 - (embedding_of_text <-> %s::vector) AS similarity
                            FROM project.cards
                            WHERE embedding_of_text IS NOT NULL
                            ORDER BY embedding_of_text <-> %s::vector ASC
                            LIMIT %s;
                            """,
                            (embedding_str, embedding_str, top_k),
                        )
                    elif distance == "cosine":
                        # <=> is cosine distance operator
                        cursor.execute(
                            """
                            SELECT
                                id,
                                name,
                                text,
                                1 - (embedding_of_text <=> %s::vector) AS similarity
                            FROM project.cards
                            WHERE embedding_of_text IS NOT NULL
                            ORDER BY embedding_of_text <=> %s::vector ASC
                            LIMIT %s;
                            """,
                            (embedding_str, embedding_str, top_k),
                        )
                    else:
                        raise ValueError(f"Invalid distance metric: {distance}. Use 'L2' or 'cosine'")

                    rows = cursor.fetchall()

                    return [
                        (
                            Card(
                                id=row["id"],
                                name=row["name"],
                                text=row["text"],
                            ),
                            float(row["similarity"])
                        )
                        for row in rows
                    ]

        except Exception as e:
            print(f"❌ Error during semantic search: {e}")
            raise

    @log
    def list_all(self) -> list[Card]:
        """
        Retrieve all cards from the project.cards table

        Returns
        -------
        list[Card]
            List of Card objects containing all cards from the database
        
        Raises
        ------
        Exception
            If database error occurs
        """
        sql_query = "SELECT id, name, text, embedding_of_text FROM project.cards"
        cards = []

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchall()

                    for row in rows:
                        card = Card(
                            id=row["id"],
                            name=row["name"],
                            text=row["text"],
                            embedding_of_text=row["embedding_of_text"],
                        )
                        cards.append(card)

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

        return cards

    @log
    def get_all_ids(self) -> list[int]:
        """
        Retrieve all IDs from the project.cards table

        Returns
        -------
        list[int]
            List of integers containing the IDs of all cards in the database
        
        Raises
        ------
        Exception
            If database error occurs
        """
        sql_query = "SELECT id FROM project.cards"
        ids = []

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchall()

                    for row in rows:
                        ids.append(row["id"])

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

        return ids
