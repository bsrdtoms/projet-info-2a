import logging
import dotenv

from utils.log_init import initialize_logs
from views.welcome_view import WelcomeView

if __name__ == "__main__":
    # Charger les variables d'environnement
    dotenv.load_dotenv(override=True)

    # Initialiser les logs
    initialize_logs("MagicSearch Application")

    # Vue de départ
    vue_courante = WelcomeView()
    nb_erreurs = 0

    while vue_courante:
        if nb_erreurs > 100:
            print("Le programme recense trop d'erreurs et va s'arrêter")
            break
        try:
            # Affichage du menu
            vue_courante = vue_courante.menu_choice()

        except Exception as e:
            logging.error(f"{type(e).__name__} : {e}", exc_info=True)
            nb_erreurs += 1
            print(
                "Une erreur est survenue, retour au menu principal.\n"
                "Consultez les logs pour plus d'informations."
            )
            vue_courante = WelcomeView()

    # Fin de l'application
    print("----------------------------------")
    print("Goodbye!")
    logging.info("Fin de l'application")
