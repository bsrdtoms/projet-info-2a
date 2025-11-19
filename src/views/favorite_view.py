from views.abstract_view import AbstractView
from service.favorite_service import FavoriteService


class FavoriteView(AbstractView):
    """Vue pour gérer les cartes favorites de l'utilisateur."""

    def __init__(self, user):
        self.user = user
        self.favorite_service = FavoriteService()

    def display(self):
        self.show_title("Your favorites")
        print("1. View all favorites")
        print("2. Add a card to favorites")
        print("3. Remove a card from favorites")
        print("4. Return to main menu")

    def menu_choice(self):
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                favorites = self.favorite_service.list_favorites(self.user.id)
                if not favorites:
                    self.show_message("You have no favorites yet.")
                else:
                    self.show_message("Your favorite cards:")
                    for fav in favorites:
                        print(f"- {fav}")
                input("\nPress Enter to continue...")

            elif choice == "2":
                card_id = self.get_input("Enter the card ID to add: ")
                success, message = self.favorite_service.add_favorite(self.user.id, int(card_id))
                self.show_message(message)
                input("\nPress Enter to continue...")

            elif choice == "3":
                card_id = self.get_input("Enter the card ID to remove: ")
                success, message = self.favorite_service.remove_favorite(self.user.id, int(card_id))
                self.show_message(message)
                input("\nPress Enter to continue...")

            elif choice == "4":
                break

            else:
                self.show_message("Invalid choice, please try again.")
