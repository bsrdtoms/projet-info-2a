```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant V as SearchView
    participant CS as CardService
    participant EA as EmbeddingAPI
    participant CD as CardDao
    participant DB as Database

    %% Step 1: Semantic search initiation
    U->>V: Enters semantic query (“flying dragon card”)
    V->>CS: semantic_search(query, limit, user_id=user_id)

    %% Step 2: Embedding generation
    rect rgba(200,200,255,0.1)
        CS->>EA: POST /embed (text)
        EA-->>CS: embedding_response
    end

    %% Step 3: SQL similarity search
    rect rgba(200,255,200,0.1)
        CS->>CD: semantic_search(query_embedding, top_k, distance)
        CD->>DB: SELECT ... ORDER BY embedding_of_text <-> embedding ASC
        DB-->>CD: cards sorted by similarity
        CD-->>CS: ordered_card_list
    end

    %% Step 4: Return results
    CS-->>V: search_results

    %% Step 5: Final display
    V->>U: Displays cards with similarity scores

