from dao.db_connection import DBConnection
from business_object.card import Card


class CardDao():
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

    def delete(self, carte) -> bool:
        """Supression d'une carte dans la base de données

        Parameters
        ----------------
        carte : CarteMagic

        Returns
        ----------------
        created : bool
            True si la suppression est un succès
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

    def search_by_name(self):
        """ 

        Parameters
        ----------------

        Returns
        ----------------

        """
        pass

    def semantic_search(self):
        """ 

        Parameters
        ----------------

        Returns
        ----------------
        
        """
        pass

    def random(self):
        """ 

        Parameters
        ----------------

        Returns
        ----------------
        
        """
        pass

    def modify(self):
        """ 

        Parameters
        ----------------

        Returns
        ----------------
        
        """
        pass

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
        sql_query = "SELECT id, name, embedding_of_text FROM project.cards"
        cards = []

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchall()  # [(id, name, embedding_of_text), ...]

                    for row in rows:
                        card = Card(id=row[0], name=row[1], embedding_of_text=row[2])
                        cards.append(card)

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

        return cards
