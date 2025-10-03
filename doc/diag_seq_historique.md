```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant V as Search view
    participant HS as Historical Service
    participant HD as Historical DAO
    participant DB as Database

    %% Étape 1: Demande d'historique
    U->>V: Click on 'access history'
    V->>HS: consult(User)

    %% Étape 2: Récupération depuis DAO
    HS->>HD: read_history(User)
    HD->>DB: SELECT * FROM search_history WHERE user_id = ?
    DB-->>HD: search_list
    HD-->>HS: user_history

    %% Étape 3: Retour des résultats
    HS-->>V: user_history

    %% Étape 4: Affichage
    V->>U: Historical display of searches (queries + associated results)
