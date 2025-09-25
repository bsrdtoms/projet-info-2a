sequenceDiagram
    participant U as User
    participant V as View
    participant S as Service
    participant D as DAO
    participant E as Embedding
    participant DB as Database
    participant H as History
    participant HD as HistoryDAO

    U->>V: Start search (text)
    V->>S: searchSemantic(query)

    S->>E: generateEmbedding(query)
    E-->>S: embedding_result
    S->>D: findSimilarCards(embedding_result)
    D->>DB: SELECT cosine_similarity
    DB-->>D: similar_cards
    D-->>S: sorted_cards

    S->>D: findByName(card_name)
    D->>DB: SELECT WHERE name LIKE "card_name"
    DB-->>D: matching_cards
    D-->>S: cards_list

    S-->>V: search_results

    V->>H: addSearch(user_id, query, results)
    H->>HD: create(entry)
    HD->>DB: INSERT search_history
    DB-->>HD: confirmation
    HD-->>H: success
    H-->>V: history_updated

    V->>U: display results (cards + similarity)
