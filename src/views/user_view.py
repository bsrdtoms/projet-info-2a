from views.abstract_view import AbstractView
from views.search_view import SearchView
from views.favorite_view import FavoriteView
from service.user_service import UserService

import logging

from service.card_service import CardService
from business_object.card import Card
# Note: the API must communicate with the service only


class UserView(AbstractView):
    """Main view for a logged-in user (client, admin, or game designer)."""

    def __init__(self, user, user_service, role="user"):
        self.user = user
        self.user_service = user_service
        self.role = role

    def display(self):
        self.show_title(f"Main menu ({self.role})")
        print("1. Access favorites")
        print("2. Access history")
        print("3. Search a card")
        print("4. Logout")

        if self.role == "admin":
            print("5. Account management")
        elif self.role == "gamedesigner":
            print("5. Card management")

    def menu_choice(self):
        while True:
            self.display()
            choice = self.get_input()

            if choice == "1":
                FavoriteView(self.user).menu_choice()
            elif choice == "2":
                pass
            elif choice == "3":
                SearchView(user=self.user).menu_choice()
            elif choice == "4":
                self.show_message("You have been logged out.")
                break
            elif choice == "5" and self.role in ["admin", "gamedesigner"]:
                if self.role == "admin":
                    self.admin_menu_choice()
                if self.role == "gamedesigner":
                    self.gamedesigner_menu_choice()
            else:
                self.show_message("Invalid choice, please try again.")

    def display_admin(self):
        self.show_title(f"Menu ({self.role})")
        print("1. Create user")
        print("2. Delete user")

    def admin_menu_choice(self):
        while True:
            self.display_admin()
            choice = self.get_input()

            if choice == "1":
                print("Please write the email of the user")
                email = self.get_input()
                print("Please write the password of the user")
                password = self.get_input()
                print("Please write the role of the user :")
                print("1 : client \n 2 : game_designer \n 3 : admin")
                d = ["client", "game_designer", "admin"]
                rep = self.get_input()
                if rep in [1, 2, 3]:
                    role = d[int(rep)]
                else:
                    print("Error : this role doesn't exist")
                print("Please write the first name of the user")
                first_name = self.get_input()
                print("Please write the last name of the user")
                last_name = self.get_input()
                UserService().create_account(email, password, first_name, last_name, role)

            elif choice == "2":
                pass
            else:
                self.show_message("Invalid choice, please try again.")

    def display_gamedesigner(self):
        self.show_title(f"Menu ({self.role})")
        print("1. Create card")
        print("2. modify card")
        print("3. Delete card")

    def gamedesigner_menu_choice(self):
        while True:
            self.display_game_designer()
            choice = self.get_input()

            # 2. ---------- USER ----------
            card_service = CardService()

            if choice == "1":
                print("Please write the name of the new card")
                name = self.get_input()
                print("Please write the text of the new card")
                text = self.get_input()

                logging.info("Creating a card")
                card_object = Card(None, name, text)

                success = card_service.add_card(card_object)
                if not success:
                    print("Error creating the card")

                return {"message": f"Card '{name}' created successfully"}

            elif choice == "2":
                print("Please write the id of the card")
                card_id = int(self.get_input())

                print("Please write the dict of updates (ex : {name : 'new name'})")
                updates = dict(self.get_input())

                logging.info(f"Modifying card {card_id}")
                card_object = card_service.find_by_id(card_id)
                success = card_service.modify_card(card_object, updates)

            elif choice == "3":
                print("Please write the id of the card")
                card_id = int(self.get_input())
                logging.info(f"Deleting card {card_id}")
                card_object = Card(card_id, None)
                success = card_service.delete_card(card_object)
            else:
                self.show_message("Invalid choice, please try again.")
