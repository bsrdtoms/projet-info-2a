from dao.db_connection import DBConnection
from business_object.card import Card


class CardDao():
    """Classe contenant les méthodes pour accéder aux Cartes de la base de données"""

    def create(self, carte) -> bool:
        """Création d'une carte dans la base de données

        Parameters
        ----------------
        carte : Card
            Objet représentant la carte à insérer

        Returns
        ----------------
        created : bool
            True si la création est un succès
            False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # On n'insère pas l'id, car il est souvent AUTO_INCREMENT
                    # embedding_of_text peut être None
                    cursor.execute(
                        """
                        INSERT INTO project.cards (name, text, embedding_of_text)
                        VALUES (%s, %s, %s)
                        """,
                        (carte.name, carte.text, carte.embedding_of_text)
                    )
            return True
        except Exception as e:
            print(f"Erreur lors de l'insertion: {e}")
            return False

    def delete(self, carte) -> bool:
        """Supression d'une carte dans la base de données

        Parameters
        ----------------
        carte : Card
            Objet représentant la carte à supprimer

        Returns
        ----------------
        deleted : bool
            True si la suppression est un succès
            False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM project.cards
                        WHERE id = %s
                        """,
                        (carte.id,)
                    )
                    # Vérifie qu'une ligne a bien été supprimée
                    if cursor.rowcount == 0:
                        print(f"Aucune carte trouvée avec l'id {carte.id} ({carte.name})")
                        return False
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False

    def find_by_id(self, id_card):
        """Trouver une carte grace à son id

        Parameters
        ----------
        id_carte : int
            numéro id de la carte que l'on souhaite trouver

        Returns
        -------
        carte : Carte
            renvoie la carte que l'on cherche par id
        """

    def search_by_name(self, name):
        """
        Recherche les cartes dont le nom contient le texte donné (insensible à la casse).

        Parameters
        ----------------
        name : str
            Le nom (ou une partie du nom) de la carte à rechercher.

        Returns
        ----------------
        cards : list[Card]
            Liste d'objets Card correspondant aux résultats de la recherche.
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
                            id=row['id'],
                            name=row['name'],
                            text=row['text'],
                            embedding_of_text=row['embedding_of_text']
                        )
                        cards.append(card)

        except Exception as e:
            print(f"Database error: {e}")
            raise

        return cards

    def modify(self, card_id: int, champ: str, valeur) -> bool:
        """
        Met à jour un champ d'une carte dans la table project.cards.

        Parameters
        ----------------
        card_id : int
            identifiant unique de la carte
        champ : str
            nom de la colonne à modifier
        valeur : any
            nouvelle valeur à affecter

        Returns
        ----------------
        created : bool
            True si la modification est un succès (au moins 1 ligne modifiée),
            False sinon.
        """
        update_sql = f"UPDATE project.cards SET {champ} = %s WHERE id = %s;"

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(update_sql, (valeur, card_id))
                    modified_rows = cursor.rowcount  # nombre de lignes affectées
                connection.commit()
            return modified_rows > 0
        except Exception as e:
            print(f"❌ SQL error: {e}")
            return False


    # vérifier comment sont les colonnes de la BDD, et quels paramètres sont attendus
    #  pour un objet de type Card
    def list_all(self):
        """
        Récupère toutes les cartes de la table project.cards.

        Returns
        ----------------
        cards : list[Carte]
            renvoie une liste d'objets Card avec toutes les cartes de la base de données.
        """
        sql_query = "SELECT id, name, text, embedding_of_text FROM project.cards"
        cards = []

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchall()  # [(id, name, embedding_of_text), ...]

                    for row in rows:
                        card = Card(id=row['id'], name=row['name'], text=row['text'], embedding_of_text=row['embedding_of_text'])
                        cards.append(card)

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

        return cards
