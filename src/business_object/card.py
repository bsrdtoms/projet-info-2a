"""
Business object representing a Magic card
"""


class Card:
    """Represents a Magic: The Gathering card"""

    def __init__(
        self,
        id: int | None,
        name: str,
        text: str | None,
        embedding_of_text: list[float] | None = None
    ):
        """
        Initialize a Magic card

        Parameters
        ----------
        id : int or None
            Unique identifier in the database (None before insertion)
        name : str
            Card name
        text : str or None
            Card description/rules text
        embedding_of_text : list[float] or None, optional
            Vector representation for semantic search (default: None)
        """
        self.id = id
        self.name = name
        self.text = text
        self.embedding_of_text = embedding_of_text

    def __str__(self) -> str:
        """
        Human-readable representation (displayed when using print(card))

        Returns
        -------
        str
            Formatted string representation of the card
        """
        text_content = self.text or ""  # Use empty string if text is None
        self.is_truncated = len(text_content) >= 100
        text_preview = (
            text_content if not self.is_truncated else text_content[:100] + "..."
        )
        
        id_display = self.id if self.id is not None else "(not saved)"
        
        return (
            f"Card {id_display}\n"
            f"Name: {self.name}\n"
            f"Text: {text_preview}"
        )

    def __repr__(self) -> str:
        """
        Technical representation of a card

        Returns
        -------
        str
            String representation for debugging
        """
        text_content = self.text or ""  # Use empty string if text is None
        text_preview = (
            text_content if len(text_content) < 100 else text_content[:100] + "..."
        )
        
        return f"Card(id={self.id}, name='{self.name}', text='{text_preview}')"