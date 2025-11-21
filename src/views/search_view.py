from views.abstract_view import AbstractView
from service.card_service import CardService


class SearchView(AbstractView):
    """View for card search (random, by name, or semantic)."""

    def display(self):
        self.show_title("Search a card")
        print("1. Random card")
        print("2. Search by name")
        print("3. Semantic search")
        print("4. Return to main menu")

    def pause(self):
        input("\nPress Enter to return to menu...")

    def menu_choice(self):
        card_service = CardService()
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                result = card_service.random()
                self.show_message(result)
                if hasattr(result, "is_truncated") and result.is_truncated:
                    choice = input("\nThe text has been abbreviated. See full text? (y/n): ")
                    if choice.lower() == "y":
                        print("\n=== Full text ===")
                        print(result.text)
                self.pause()

            elif choice == "2":
                name = self.get_input("Enter the card name: ")
                result = card_service.search_by_name(name)
                for card in result:
                    self.show_message(card)
                self.pause()

            elif choice == "3":
                query = self.get_input("Describe the card you're looking for: ")
                limit_input = self.get_input("How many results do you want? (default = 3): ")
                # If the user just presses Enter, we use 3
                try:
                    limit = int(limit_input) if limit_input.strip() else 3
                except ValueError:
                    limit = 3  # in case of invalid value
                result = card_service.semantic_search(query, limit)
                for card, similarity in result:
                    self.show_message(card)
                    print(f"Similarity: {similarity:.4f}\n")
                self.pause()

            elif choice == "4":
                break
            else:
                self.show_message("Invalid choice, please try again.")
                self.pause()
