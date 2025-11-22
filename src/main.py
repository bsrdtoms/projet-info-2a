import logging
import dotenv
from utils.log_init import initialize_logs
from views.welcome_view import WelcomeView

if __name__ == "__main__":
    # Load environment variables
    dotenv.load_dotenv(override=True)

    # Initialize logs
    initialize_logs("MagicSearch Application")

    # Starting view
    current_view = WelcomeView()
    error_count = 0

    while current_view:
        if error_count > 100:
            print("The program has encountered too many errors and will stop")
            break
        try:
            # Display menu
            current_view = current_view.menu_choice()

        except Exception as e:
            logging.error(f"{type(e).__name__} : {e}", exc_info=True)
            error_count += 1
            print(
                "An error occurred, returning to main menu.\n"
                "Check the logs for more information."
            )
            current_view = WelcomeView()

    # End of application
    print("----------------------------------")
    print("Goodbye!")
    logging.info("End of application")
