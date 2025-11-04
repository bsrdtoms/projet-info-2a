"""
DAO pour les cartes Magic avec support pgvector
Remplace src/dao/card_dao.py
"""

from dao.db_connection import DBConnection
from business_object.card import Card


class CardDao:
    """Classe contenant les méthodes pour accéder aux Cartes de la base de données"""

    def create(self, carte) -> bool:
        """
        Création d'une carte dans la base de données

        Parameters
        ----------
        carte : Card
            Carte à insérer

        Returns
        -------
        bool
            True si la création est un succès, False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Convertir l'embedding en format pgvector
                    embedding_str = None
                    if carte.embedding_of_text:
                        embedding_str = (
                            "[" + ",".join(str(f) for f in carte.embedding_of_text) + "]"
                        )

                    cursor.execute(
                        """
                        INSERT INTO project.cards (name, type, text, embedding_of_text)
                        VALUES (%s, %s, %s, %s::vector)
                        """,
                        (carte.name, carte.type, carte.text, embedding_str),
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion: {e}")
            return False

    def delete(self, carte) -> bool:
        """
        Suppression d'une carte dans la base de données

        Parameters
        ----------
        carte : Card

        Returns
        -------
        bool
            True si la suppression est un succès, False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM project.cards WHERE id = %s",
                        (carte.id,),
                    )
                connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False

    def find_by_id(self, id_card: int):
        """
        Trouver une carte grâce à son id

        Parameters
        ----------
        id_card : int
            Numéro id de la carte que l'on souhaite trouver

        Returns
        -------
        Card ou None
            Renvoie la carte trouvée ou None
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, name, text, embedding_of_text FROM project.cards WHERE id = %s",
                        (id_card,),
                    )
                    row = cursor.fetchone()
                    if row:
                        return Card(
                            id=row["id"],
                            name=row["name"],
                            text=row["text"],
                            embedding_of_text=row["embedding_of_text"],
                        )
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return None

    def search_by_name(self, name: str, limit: int = 10):
        """
        Rechercher des cartes par nom (recherche partielle)

        Parameters
        ----------
        name : str
            Nom ou partie du nom à chercher
        limit : int
            Nombre maximum de résultats

        Returns
        -------
        list[Card]
            Liste des cartes correspondantes
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, name, text, embedding_of_text 
                        FROM project.cards 
                        WHERE name ILIKE %s
                        LIMIT %s
                        """,
                        (f"%{name}%", limit),
                    )
                    rows = cursor.fetchall()
                    return [
                        Card(
                            id=row["id"],
                            name=row["name"],
                            text=row["text"],
                            embedding_of_text=row["embedding_of_text"],
                        )
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []

    def semantic_search(self, query_embedding: list[float], top_k: int = 5):
        """
        Recherche sémantique utilisant pgvector (OPTIMISÉ!)

        Parameters
        ----------
        query_embedding : list[float]
            Embedding du texte de recherche
        top_k : int
            Nombre de résultats à retourner

        Returns
        -------
        list[dict]
            Liste de dictionnaires avec id, name, text, similarity
        """
        try:
            # Convertir l'embedding en format pgvector
            embedding_str = "[" + ",".join(str(f) for f in query_embedding) + "]"

            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Utilisation de l'opérateur <=> de pgvector
                    # Plus petit = plus similaire (distance cosinus)
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
                    rows = cursor.fetchall()

                    return [
                        {
                            "id": row["id"],
                            "name": row["name"],
                            "text": row["text"],
                            "similarity": float(row["similarity"]),
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Erreur lors de la recherche sémantique: {e}")
            raise

    def random(self):
        """
        Récupérer une carte aléatoire

        Returns
        -------
        Card ou None
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, name, text, embedding_of_text 
                        FROM project.cards 
                        ORDER BY RANDOM() 
                        LIMIT 1
                        """
                    )
                    row = cursor.fetchone()
                    if row:
                        return Card(
                            id=row["id"],
                            name=row["name"],
                            text=row["text"],
                            embedding_of_text=row["embedding_of_text"],
                        )
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération aléatoire: {e}")
            return None

    def modify(self, card_id: int, champ: str, valeur) -> bool:
        """
        Met à jour un champ d'une carte dans la table project.cards.

        Parameters
        ----------
        card_id : int
            Identifiant unique de la carte
        champ : str
            Nom de la colonne à modifier
        valeur : any
            Nouvelle valeur à affecter

        Returns
        -------
        bool
            True si la modification est un succès (au moins 1 ligne modifiée), False sinon
        """
        # Gestion spéciale pour les embeddings
        if champ == "embedding_of_text" and isinstance(valeur, list):
            valeur = "[" + ",".join(str(f) for f in valeur) + "]"
            update_sql = f"UPDATE project.cards SET {champ} = %s::vector WHERE id = %s;"
        else:
            update_sql = f"UPDATE project.cards SET {champ} = %s WHERE id = %s;"

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(update_sql, (valeur, card_id))
                    modified_rows = cursor.rowcount
                connection.commit()
            return modified_rows > 0
        except Exception as e:
            print(f"❌ SQL error: {e}")
            return False

    def list_all(self):
        """
        Récupère toutes les cartes de la table project.cards.

        Returns
        -------
        list[Card]
            Liste d'objets Card avec toutes les cartes de la base de données
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