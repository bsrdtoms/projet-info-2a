import logging
from abc import ABC, abstractmethod

class AbstractView(ABC):
    """
    Classe de base pour toutes les vues CLI.
    Fournit les méthodes génériques d'affichage et de saisie utilisateur.
    """

    def __init__(self, message=""):
        self.message = message
        logging.info(f"Vue créée : {type(self).__name__}")

    @abstractmethod
    def display(self):
        """
        Méthode abstraite : chaque vue doit définir son affichage propre.
        """
        pass

    @abstractmethod
    def menu_choice(self):
        """
        Méthode abstraite : chaque vue doit gérer la logique selon le choix utilisateur (exemple : appeler la vue suivante ou un service).
        """
        pass

    def get_input(self, message="Enter your choice: "):
        """Demande une saisie utilisateur avec un message."""
        return input(message)

    def show_message(self, message):
        """Affiche un message formaté."""
        print(f"\n{message}")

    def show_title(self, title):
        """Affiche un titre."""
        print("\n" + "=" * (len(title) + 8))
        print(f"=== {title} ===")
        print("=" * (len(title) + 8))
