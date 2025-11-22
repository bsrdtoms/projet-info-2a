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

        +add_card(name: str, text: str | None)
        +modify_card(card: Card, updates: dict)
        +delete_card(card: Card)
        +describe_card(card_id: int)
        +search_by_name(name: str)
        +find_by_id(card_id: int)
        +semantic_search(text: str, top_k: int = 5, distance: str = "L2", user_id: int = None)
        +random()
    }

    class CardDao {
        +create(card: Card)
        +delete(card: Card)
        +modify_card(card: Card, updates: dict)
        +get_card_details(card_id: int)
        +list_all()
        +get_all_ids()
        +find_by_id(card_id: int)
        +search_by_name(name: str)
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

    CardDao ..> Card : manipulate

    CardService ..> Card : manipulate

    


