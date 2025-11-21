from views.abstract_view import AbstractView
from views.search_view import SearchView
from views.user_view import UserView
from service.user_service import UserService

from getpass import getpass


class WelcomeView(AbstractView):
    """Welcome view for the application"""

    def __init__(self):
        self.user_service = UserService()

    def display(self):
        self.show_title("MAGICSEARCH")
        print("1. Search for a card (guest)")
        print("2. Create an account")
        print("3. Log in")
        print("4. Leave the application")

    def create_account_flow(self):
        """Account creation flow"""
        self.show_title("Create an account")

        email = self.get_input("Email: ")
        password = getpass("Password (min 6 characters): ") # Thanks to getpass() the password is not displayed when the user types it
        password_confirm = getpass("Confirm password: ")
        
        if password != password_confirm:
            self.show_message("❌ Passwords do not match")
            input("\nPress Enter to continue...")
            return
        
        first_name = self.get_input("First name (optional): ")
        last_name = self.get_input("Last name (optional): ")
        
        success, message, user = self.user_service.create_account(
            email=email,
            password=password,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None
        )
        
        self.show_message(message)
        input("\nPress Enter to continue...")
        
        if success:
            self.show_message("You can now log in with your credentials")

    def login_flow(self):
        """Login flow"""
        self.show_title("Log in")

        email = self.get_input("Email: ")
        password = getpass("Password: ")

        success, message, session = self.user_service.login(email, password)
        self.show_message(message)

        if success:
            input("\nPress Enter to continue...")
            # Redirect to user interface
            user = self.user_service.get_current_user()
            UserView(user=user, user_service=self.user_service, role=user.user_type).menu_choice()
        else:
            input("\nPress Enter to continue...")

    def menu_choice(self):
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                SearchView().menu_choice()
            elif choice == "2":
                self.create_account_flow()
            elif choice == "3":
                self.login_flow()
            elif choice == "4":
                self.show_message("Goodbye!")
                break
            else:
                self.show_message("Invalid choice, please try again.")