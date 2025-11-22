```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant V as SearchView
    participant CS as CardService
    participant CD as CardDao
    participant DB as Database

    %% Étape 1: Initiation recherche sémantique
    U->>V: Enters semantic query (“flying dragon card”)
    V->>CS: semantic_search(query, limit, user_id=user_id)

    %% Étape 2: Génération de l'embedd
    rect rgba(200,200,255,0.1)
        CS->>CS: get_embedding(text)<br/>(appel interne via requests)
        CS-->>CS: embedding_requete
    end

    %% Étape 3: Recherche par similarité en SQL
    rect rgba(200,255,200,0.1)
        CS->>CD: semantic_search(query_embedding, top_k, distance)
        CD->>DB: SELECT ... ORDER BY embedding_of_text <-> embedding ASC
        DB-->>CD: cartes triées par similarité
        CD-->>CS: liste_cartes_ordonnee
    end

    %% Étape 4: Retour résultats
    CS-->>V: resultats_recherche

    %% Étape 6: Affichage final
    V->>U: Affiche cartes avec scores de similarité
