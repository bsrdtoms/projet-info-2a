"""
Service layer for card operations with embedding support
"""

import random
import re
from technical_components.embedding.ollama_embedding import get_embedding
from dao.card_dao import CardDao
from business_object.card import Card
from utils.log_decorator import log


class CardService:
    """Service to manage card operations"""

    def __init__(self):
        self.dao = CardDao()

    @log
    def add_card(self, name: str, text: str | None) -> bool:
        """
        Add a card by generating its embedding before insertion

        Parameters
        ----------
        name : str
            The name of the card.
        text : str
            The textual content of the card from which the embedding will be generated.


        Returns
        -------
        bool
            True if successful, False otherwise
        """
        card = Card(None, name, text)
        try:
            # Generate embedding if text exists
            if card.text:
                embedding_response = get_embedding(card.text)
                card.embedding_of_text = embedding_response["embeddings"][0]

            # Persist via DAO
            print(f"Creating card: {card.name}")
            return self.dao.create(card)

        except Exception as e:
            print(f"❌ Unable to add card: {e}")
            return False

    @log
    def modify_card(self, card: Card, updates: dict) -> bool:
        """
        Modify specified fields of an existing card

        Parameters
        ----------
        card : Card
            Card to modify
        updates : dict
            Dictionary {column: new_value} to update

        Returns
        -------
        bool
            True if modification is successful, False otherwise
        """
        print(f"Attempting to modify card ID {card.id}...")
        success = self.dao.modify_card(card, updates)
        if success:
            print("✅ Card modified successfully")
        else:
            print("❌ Modification failed")
        return success

    @log
    def delete_card(self, card: Card) -> bool:
        """
        Delete a card from the database

        Parameters
        ----------
        card : Card
            Card object to delete

        Returns
        -------
        bool
            True if deletion succeeded, False otherwise
        """
        print(f"Attempting to delete card: {card.name} (id={card.id})")
        return self.dao.delete(card)

    @log
    def describe_card(self, card_id: int) -> str:
        """
        Generate a natural language description of a card

        Parameters
        ----------
        card_id : int
            ID of the card to describe

        Returns
        -------
        str
            A sentence describing the card

        Example
        -------
        >>> service.describe_card(1234)
        "Lightning Bolt is a red Instant that costs {R}. Lightning Bolt deals 3 damage to any target."
        """
        try:
            # Get card details from DAO
            details = self.dao.get_card_details(card_id)

            if not details:
                return f"Card with ID {card_id} not found."

            # Build the description
            description_parts = []

            # Card name and types
            name = details["name"]
            card_type = details["type"] or "Card"

            # Add color adjective before type if present
            if details["colors"] and len(details["colors"]) == 1:
                color = details["colors"][0].lower()
                # Insert color before the main type
                # Example: "Creature" -> "blue Creature"
                # But not for "Legendary Creature" -> keep "Legendary blue Creature"
                type_parts = card_type.split()
                main_types = [
                    "Creature",
                    "Instant",
                    "Sorcery",
                    "Enchantment",
                    "Artifact",
                    "Planeswalker",
                    "Land",
                ]

                for i, part in enumerate(type_parts):
                    if any(mt in part for mt in main_types):
                        type_parts.insert(i, color)
                        break
                else:
                    # If no main type found, add at the beginning
                    type_parts.insert(0, color)
                card_type = " ".join(type_parts)

            elif details["colors"] and len(details["colors"]) > 1:
                colors = ", ".join([c.lower() for c in details["colors"]])
                type_parts = card_type.split()
                main_types = [
                    "Creature",
                    "Instant",
                    "Sorcery",
                    "Enchantment",
                    "Artifact",
                    "Planeswalker",
                    "Land",
                ]

                for i, part in enumerate(type_parts):
                    if any(mt in part for mt in main_types):
                        type_parts.insert(i, f"multicolor ({colors})")
                        break
                else:
                    type_parts.insert(0, f"multicolor ({colors})")
                card_type = " ".join(type_parts)

            description_parts.append(f"{name} is a {card_type}")

            # Add mana cost if present
            if details["mana_cost"]:
                description_parts.append(f"that costs {details['mana_cost']}")

            # Join first part
            first_sentence = " ".join(description_parts) + "."

            # Add power/toughness for creatures
            if details["power"] and details["toughness"]:
                first_sentence += (
                    f" It is a {details['power']}/{details['toughness']} creature."
                )

            # Add loyalty for planeswalkers
            if details["loyalty"]:
                first_sentence += f" It has {details['loyalty']} loyalty."

            # Add card text if present
            result = first_sentence
            if details["text"]:
                text = details["text"]

                # Remove reminder text (in parentheses) for cleaner output
                text_cleaned = re.sub(r"\([^)]*\)", "", text)
                # Remove extra spaces
                text_cleaned = " ".join(text_cleaned.split())

                # Truncate if too long (keep first sentence or 200 chars)
                if len(text_cleaned) > 200:
                    # Try to cut at sentence end
                    sentences = text_cleaned.split(". ")
                    if sentences[0] and len(sentences[0]) < 200:
                        text_cleaned = sentences[0] + "."
                    else:
                        text_cleaned = text_cleaned[:200] + "..."

                result += f" {text_cleaned}"

            return result

        except Exception as e:
            print(f"❌ Error describing card: {e}")
            return f"Error: Could not describe card {card_id}"

    @log
    def search_by_name(self, name: str) -> list[Card]:
        """
        Search for cards whose name contains the given text

        Parameters
        ----------
        name : str
            Name (or partial name) of the card to search for

        Returns
        -------
        list[Card]
            List of Card objects matching the search criteria

        Raises
        ------
        ValueError
            If name is not a non-empty string
        """
        if not name or not isinstance(name, str):
            raise ValueError("Card name must be a non-empty string")

        cards_found = self.dao.search_by_name(name)

        if not cards_found:
            print(f"❌ No cards found for '{name}'")
            return []

        return cards_found

    @log
    def find_by_id(self, card_id: int) -> Card:
        """
        Find a card by its ID

        Parameters
        ----------
        card_id : int
            ID of the card to search for

        Returns
        -------
        Card or None
            Card object corresponding to the search result, or None if not found

        Raises
        ------
        ValueError
            If card_id is not an integer
        """
        if not isinstance(card_id, int):
            raise ValueError("Card ID must be an integer")

        card_found = self.dao.find_by_id(card_id)

        if not card_found:
            print(f"❌ No card found for ID '{card_id}'")
            return None

        return card_found

    @log
    def semantic_search(
        self, text: str, top_k: int = 5, distance: str = "L2", user_id: int = None
    ) -> list[tuple[Card, float]]:
        """
        Optimized semantic search using pgvector
        AVEC ENREGISTREMENT AUTOMATIQUE DE L'HISTORIQUE

        BEFORE: Retrieved all cards, calculated in Python (slow)
        AFTER: All computation done in SQL (fast)

        Parameters
        ----------
        text : str
            Search text
        top_k : int, optional
            Number of results to return (default: 5)
        distance : str, optional
            Distance metric: "L2" or "cosine" (default: "L2")
        user_id : int, optional
            ID of the user (if provided, search is logged to history)

        Returns
        -------
        list[tuple[Card, float]]
            List of tuples (Card, similarity_score)

        Raises
        ------
        Exception
            If embedding generation or database query fails
        """
        try:
            # Generate embedding for search text
            embedding_response = get_embedding(text)
            query_embedding = embedding_response["embeddings"][0]

            # Direct SQL search via pgvector (FAST!)
            # No Python loop or pandas needed!
            results = self.dao.semantic_search(query_embedding, top_k, distance)

            # NOUVEAU: Enregistrer dans l'historique si user_id fourni
            if user_id is not None:
                try:
                    from service.historical_service import HistoricalService

                    history_service = HistoricalService()
                    history_service.add_search(
                        user_id=user_id,
                        query_text=text,
                        result_count=len(results),
                        query_embedding=None,  # On ne sauvegarde pas l'embedding pour économiser de l'espace
                    )
                except Exception as e:
                    print(f"⚠️  Warning: Could not save to history: {e}")
                    # Ne pas lever l'erreur, continuer quand même

            return results

        except Exception as e:
            print(f"❌ Error during semantic search: {e}")
            raise

    @log
    def random(self) -> Card:
        """
        Retrieve a random card from the database

        Returns
        -------
        Card or None
            Random Card object, or None if no cards exist
        """
        ids = self.dao.get_all_ids()
        if not ids:
            print("❌ No cards found in database")
            return None

        random_id = random.choice(ids)
        return self.dao.find_by_id(random_id)
