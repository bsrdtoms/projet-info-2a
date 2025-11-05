from views.abstract_view_bis import AbstractView
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
        self.display()
        choice = self.get_input()

        if choice == "1":
            return SearchView()  # Retourne la vue suivante
        elif choice == "2":
            self.show_message("Exploring clusters...")
            return self      # On reste dans la même vue
        elif choice == "3":
            self.show_message("Creating an account...")
            return self
        elif choice == "4":
            self.show_message("Logging in...")
            return self
        elif choice == "5":
            self.show_message("Goodbye!")
            return None  # Quitte l'application
        else:
            self.show_message("Invalid choice, please try again.")
            return self
