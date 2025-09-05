```mermaid
erDiagram
    USER {
        int user_id PK
        varchar email UK
        varchar password_hash
        varchar first_name
        varchar last_name
        enum user_type "end_user, game_designer, admin"
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    CARD {
        int card_id PK
        varchar card_name UK
        text card_text
        varchar mana_cost
        varchar card_type
        varchar rarity
        varchar set_code
        int power
        int toughness
        text flavor_text
        varchar image_url
        datetime created_at
        datetime updated_at
        int created_by FK
    }

    CARD_EMBEDDING {
        int embedding_id PK
        int card_id FK
        vector embedding_vector "Vector de dimension 1536 ou autre"
        varchar embedding_model "modèle utilisé (OpenAI, etc.)"
        datetime created_at
        datetime updated_at
    }

    FAVORITE {
        int favorite_id PK
        int user_id FK
        int card_id FK
        datetime created_at
    }

    MATCH_REQUEST {
        int request_id PK
        int user_id FK
        text input_text
        datetime created_at
        varchar session_id
    }

    MATCH_RESULT {
        int result_id PK
        int request_id FK
        int card_id FK
        float similarity_score
        int rank_position
        datetime created_at
    }

    TEXT_EMBEDDING {
        int text_embedding_id PK
        int request_id FK
        vector text_vector "Vector de l'input text"
        varchar embedding_model
        datetime created_at
    }

    SESSION {
        varchar session_id PK
        int user_id FK
        datetime created_at
        datetime last_activity
        boolean is_active
    }

    %% Relations
    USER ||--o{ CARD : "created_by"
    USER ||--o{ FAVORITE : "user_id"
    USER ||--o{ MATCH_REQUEST : "user_id"
    USER ||--o{ SESSION : "user_id"
    
    CARD ||--|| CARD_EMBEDDING : "card_id"
    CARD ||--o{ FAVORITE : "card_id"
    CARD ||--o{ MATCH_RESULT : "card_id"
    
    MATCH_REQUEST ||--o{ MATCH_RESULT : "request_id"
    MATCH_REQUEST ||--|| TEXT_EMBEDDING : "request_id"
    
    SESSION ||--o{ MATCH_REQUEST : "session_id"
