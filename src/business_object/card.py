class Card:
    
    def __init__(self, id: int, name: str, text: str, embedding_of_text=None):
        self.id = id
        self.name = name
        self.text = text
        self.embedding_of_text = embedding_of_text
