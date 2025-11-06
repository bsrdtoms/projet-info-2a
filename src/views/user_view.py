from views.abstract_view import AbstractView
from views.search_view import SearchView
from views.favorite_view import FavoriteView



class UserView(AbstractView):
    """Vue principale pour un utilisateur connecté (client, admin ou game designer)."""

    def __init__(self, role="user"):
        self.role = role

    def display(self):
        self.show_title(f"Main menu ({self.role})")
        print("1. Access favorites")
        print("2. Access history")
        print("3. Search a card")
        print("4. Manage your account")
        print("5. Logout")

        if self.role == "admin":
            print("6. Account management")
        elif self.role == "gamedesigner":
            print("6. Card management")

    def menu_choice(self):
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                FavoriteView(self.user).menu_choice()
            elif choice == "2":
                pass
            elif choice == "3":
                SearchView().menu_choice()
            elif choice == "4":
                pass
            elif choice == "5":
                self.show_message("You have been logged out.")
                break
            elif choice == "6" and self.role in ["admin", "gamedesigner"]:
                pass
            else:
                self.show_message("Invalid choice, please try again.")
