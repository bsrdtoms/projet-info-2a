class CarteMagicDao():
    """Classe contenant les méthodes pour accéder aux Cartes de la base de données"""

    def créer(self, carte) -> bool :
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

    def trouver_par_id(self, id_carte) -> Carte :
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
