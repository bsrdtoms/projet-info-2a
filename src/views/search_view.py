from views.abstract_view import AbstractView
from service.card_service import CardService


class SearchView(AbstractView):
    """Vue pour la recherche de cartes (aléatoire, par nom, ou sémantique)."""

    def display(self):
        self.show_title("Search a card")
        print("1. Random card")
        print("2. Search by name")
        print("3. Semantic search")
        print("4. Return to main menu")

    def pause(self):
        input("\nAppuie sur Entrée pour revenir au menu...")

    def menu_choice(self):
        card_service = CardService()
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                result = card_service.random()
                self.show_message(result)
                self.pause()

            elif choice == "2":
                name = self.get_input("Enter the card name: ")
                result = card_service.search_by_name(name)
                for card in result:
                    self.show_message(card)
                self.pause()

            elif choice == "3":
                query = self.get_input("Describe the card you're looking for: ")
                result = card_service.semantic_search(query)
                self.show_message(result)
                self.pause()

            elif choice == "4":
                break
            else:
                self.show_message("Invalid choice, please try again.")
                self.pause()
