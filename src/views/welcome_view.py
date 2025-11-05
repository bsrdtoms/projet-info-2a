from views.abstract_view import AbstractView
from views.search_view import SearchView
                

class WelcomeView(AbstractView):
    def display(self):
        self.show_title("MAGICSEARCH")
        print("1. Search for a card")
        print("2. Explore clusters")
        print("3. Create an account")
        print("4. Log in")
        print("5. Leave the application")

    def menu_choice(self):
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                SearchView().menu_choice()
            elif choice == "2":
                pass
            elif choice == "3":
                self.show_message("Creating an account...")
                pass
            elif choice == "4":
                self.show_message("Logging in...")
                pass
            elif choice == "5":
                return None
            else:
                self.show_message("Invalid choice, please try again.")
