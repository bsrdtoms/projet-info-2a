import logging
from abc import ABC, abstractmethod


class AbstractView(ABC):
    """
    Base class for all CLI views.
    Provides generic methods for display and user input.
    """

    def __init__(self, message=""):
        self.message = message
        logging.info(f"View created: {type(self).__name__}")

    @abstractmethod
    def display(self):
        """
        Abstract method: each view must define its own display.
        """
        pass

    @abstractmethod
    def menu_choice(self):
        """
        Abstract method: each view must handle logic based on user choice (example: call the next view or a service).
        """
        pass

    def get_input(self, message="Enter your choice: "):
        """Requests user input with a message."""
        return input(message)

    def show_message(self, message):
        """Displays a formatted message."""
        print(f"\n{message}")

    def show_title(self, title):
        """Displays a title."""
        print("\n" + "=" * (len(title) + 8))
        print(f"=== {title} ===")
        print("=" * (len(title) + 8))
