```mermaid
%% Définition des classes
classDiagram
    class USER {
        int user_id
        string email
        string first_name
        string last_name
        string user_type
        bool is_active
    }

    class CARD {
        int card_id
        string card_name
        string card_text
        string mana_cost
        string card_type
        string rarity
    }

    class CARD_EMBEDDING {
        int embedding_id
    }

    class FAVORITE {
        int favorite_id
    }

    class MATCH_REQUEST {
        int request_id
        string input_text
    }

    class MATCH_RESULT {
        int result_id
        float similarity_score
        int rank_position
    }

    class TEXT_EMBEDDING {
        int text_embedding_id
    }

    class SESSION {
        string session_id
        datetime last_activity
        bool is_active
    }

%% Relations entre classes
    USER "1" --> "*" CARD : crée
    USER "1" --> "*" FAVORITE : possède
    USER "1" --> "*" MATCH_REQUEST : fait
    USER "1" --> "*" SESSION : possède

    CARD "1" --> "1" CARD_EMBEDDING : a
    CARD "1" --> "*" FAVORITE : apparaît dans
    CARD "1" --> "*" MATCH_RESULT : apparaît dans

    MATCH_REQUEST "1" --> "*" MATCH_RESULT : contient
    MATCH_REQUEST "1" --> "1" TEXT_EMBEDDING : a

    SESSION "1" --> "*" MATCH_REQUEST : contient
