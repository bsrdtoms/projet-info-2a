from dao.db_connection import DBConnection

class FavoriteDAO:
    def add_favorite(self, user_id: int, card_id: int) -> bool:
        """Ajoute une carte aux favoris d'un utilisateur"""
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

    def remove_favorite(self, user_id: int, card_id: int) -> bool:
        """Supprime une carte des favoris"""
        query = "DELETE FROM project.favorites WHERE user_id = %s AND card_id = %s;"
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id, card_id))
                connection.commit()
                return cursor.rowcount > 0

    def list_favorites(self, user_id: int) -> list[dict]:
        """Récupère toutes les cartes favorites d’un utilisateur"""
        query = """
        SELECT f.card_id, c.name, c.type, c.mana_cost
        FROM project.favorites f
        JOIN project.cards c ON f.card_id = c.id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC;
        """
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
                if not rows:
                    return []
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    def is_favorite(self, user_id: int, card_id: int) -> bool:
        """Vérifie si une carte est déjà en favoris"""
        query = "SELECT 1 FROM project.favorites WHERE user_id = %s AND card_id = %s;"
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id, card_id))
                return cursor.fetchone() is not None
