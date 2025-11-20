from dao.db_connection import DBConnection
from business_object.card import Card
from utils.log_decorator import log


class FavoriteDAO:

    @log
    def add_favorite(self, user_id: int, card_id: int) -> bool:
        """Ajoute une carte aux favoris d'un utilisateur"""
        try:
            query = """
            INSERT INTO project.favorites (user_id, card_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, card_id) DO NOTHING;
            """
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (user_id, card_id))
                    connection.commit()
                    return cursor.rowcount > 0  # True si ajouté, False si déjà existant
        except Exception as e:
            print(f"❌ Erreur ajout de la carte aux favoris: {e}")
            return False    

    @log
    def remove_favorite(self, user_id: int, card_id: int) -> bool:
        """Supprime une carte des favoris"""
        try:
            query = "DELETE FROM project.favorites WHERE user_id = %s AND card_id = %s;"
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (user_id, card_id))
                    connection.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Erreur suppression de la carte des favoris: {e}")
            return False

    @log
    def list_favorites(self, user_id: int) -> list[dict]:
        """Récupère toutes les cartes favorites d’un utilisateur"""
        query = """
        SELECT f.card_id, c.id, c.name, c.text, c.embedding_of_text
        FROM project.favorites f
        JOIN project.cards c ON f.card_id = c.id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC;
        """
        cards = []

        try :
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (user_id,))
                    rows = cursor.fetchall()

                    if not rows:
                        return []

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