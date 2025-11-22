```mermaid
classDiagram
    %% ====================
    %% VUES 
    %% ====================
    class AbstractView {
        +display()
        +menu_choice()
        +get_input(message)
        +show_message(message)
        +show_title(title)
    }

    class SearchView {
        +display()
        +pause()
        +menu_choice()
    }

    AbstractView <|-- SearchView
    

    %% ====================
    %% CARTES
    %% ====================
    class CardService {
        +dao : CardDao
        +semantic_search(text: str, top_k: int = 5, distance: str = "L2", user_id: int = None)
    }

    class CardDao {
        +semantic_search(query_embedding: list[float], top_k: int = 5, distance: str = "L2")
    }

    class Card {
        +id: int | None,
        +name: str,
        +text: str | None,
        +embedding_of_text: list[float] | None = None
        +__str__()
        +__repr__()
    }

    SearchView ..> CardService : use

    CardService ..> CardDao : use

    CardService ..> Card : manipulate
    CardDao ..> Card : manipulate
