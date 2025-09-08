mermaid_code = """
erDiagram
    CARD {
        int id PK
        string name
        string type
        string color
        string text
        list<float> vector_embedding
    }
    SET {
        int id PK
        string name
        date release_date
    }
    TYPE {
        int id PK
        string name
    }

    SET ||--o{ CARD : "contient"
    CARD }o--o{ TYPE : "a"
"""

with open("magicsearch_erd.md", "w", encoding="utf-8") as f:
    f.write("```mermaid\n")
    f.write(mermaid_code)
    f.write("\n```")

print("Code Mermaid généré : magicsearch_erd.md")
