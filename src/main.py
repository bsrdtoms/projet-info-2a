import argparse     # Sert à lire les arguments passés au lancement (ex: --mode api)
from views.welcome_view import WelcomeView


def main():
    parser = argparse.ArgumentParser(description="MagicSearch Application")
    parser.add_argument("--mode", choices=["cli", "api"], default="cli",
                        help="Mode d'exécution : CLI ou API (défaut: CLI)")
    args = parser.parse_args()

    if args.mode == "cli":
        WelcomeView().menu_choice()

    elif args.mode == "api":
        pass

if __name__ == "__main__":
    main()