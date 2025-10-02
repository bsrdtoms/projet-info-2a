from dao.db_connection import DBConnection
import pandas as pd


class MagicCardDao():
    """Classe contenant les méthodes pour accéder aux Cartes de la base de données"""

    def create(self, carte) -> bool:
        """Création d'une carte dans la base de données

        Parameters
        ----------------
        carte : CarteMagic

        Returns
        ----------------
        created : bool
            True si la création est un succès
            False sinon
        """
        pass

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

    def get_all_embeddings(self):
        sql_query = "SELECT id, name, embedding_of_text FROM project.cards"

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchall()  # rows = [(id, name, embedding_of_text), ...]
                    colnames = [desc[0] for desc in cursor.description]  # récupère les noms des colonnes
        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

        if not rows:
            print("⚠️ No cards found in database.")
            return pd.DataFrame(columns=["id", "name", "embedding_of_text"])  # DataFrame vide

        # Construction du DataFrame
        df = pd.DataFrame(rows, columns=colnames)

        return df
