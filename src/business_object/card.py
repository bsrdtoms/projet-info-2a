class Card:

    def __init__(
        self, id: int | None, name: str, text: str | None, embedding_of_text=None
    ):
        """
        Représente une carte Magic.

        Parameters
        ----------------
        id : int | None
            Identifiant unique dans la base (None avant insertion)
        name : str
            Nom de la carte
        text : str
            Description de la carte
        embedding_of_text : any
            Représentation vectorielle (optionnelle)
        """
        self.id = id
        self.name = name
        self.text = text
        self.embedding_of_text = embedding_of_text

    def __str__(self):
        """
        Représentation lisible (affichée quand on fait print(card)).
        """
        texte = self.text or ""  # si self.text est None, on met une chaîne vide
        self.is_truncated = len(texte) >= 100
        text_preview = texte if len(texte) < 100 else texte[:100] + "..."
        return (
            f"Carte {self.id if self.id is not None else '(non enregistrée)'}\n"
            f"Nom : {self.name}\n"
            f"Texte : {text_preview}"
        )

    def __repr__(self):
        """
        Représentation technique d'une carte.
        """
        texte = self.text or ""  # si self.text est None, on met une chaîne vide
        text_preview = texte if len(texte) < 100 else texte[:100] + "..."
        return f"Card(id={self.id}, name='{self.name}', text='{text_preview}'"
