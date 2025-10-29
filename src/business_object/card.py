class Card:
    
    def __init__(self, id: int, name: str, text: str, embedding_of_text=None):
        self.id = id
        self.name = name
        self.text = text
        self.embedding_of_text = embedding_of_text

    def __str__(self):
        """
        Représentation lisible (affichée quand on fait print(card)).
        """
        texte = self.text or ""  # si self.text est None, on met une chaîne vide
        text_preview = texte if len(texte) < 100 else texte[:100] + "..."
        return (
            f"Carte {self.id}\n"
            f"Nom : {self.name}\n"
            f"Texte : {text_preview}"
        )

    def __repr__(self):
        """
        Représentation technique d'une carte.
        """
        return f"Card(id={self.id}, name='{self.name}', text='{self.text[:30]}...', embedding={'Yes' if self.embedding_of_text else 'No'})"

