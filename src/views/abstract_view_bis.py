import logging
from abc import ABC, abstractmethod


class AbstractView(ABC):
    """
    Classe de base pour toutes les vues CLI.
    Combine ton style et le modèle du prof.
    """

    def __init__(self, message=""):
        """
        Initialise la vue avec un message facultatif et log la création.
        """
        self.message = message
        logging.info(f"Vue créée : {type(self).__name__}")

    def nettoyer_console(self):
        """
        Simule un nettoyage de console en affichant plusieurs lignes vides.
        """
        print("\n" * 30)

    def afficher(self):
        """
        Affiche le message de la vue après avoir nettoyé la console.
        """
        self.nettoyer_console()
        if self.message:
            print(self.message)
            print()

    def show_title(self, title):
        """Affiche un titre formaté."""
        print("\n" + "=" * (len(title) + 8))
        print(f"=== {title} ===")
        print("=" * (len(title) + 8))

    def show_message(self, message):
        """Affiche un message formaté."""
        print(f"\n{message}")

    def get_input(self, message="Enter your choice: "):
        """Demande une saisie utilisateur."""
        return input(message)

    @abstractmethod
    def menu_choice(self):
        """
        Méthode abstraite : chaque vue doit gérer la logique selon le choix utilisateur.
        Doit retourner la vue suivante ou None pour quitter.
        """
        pass
