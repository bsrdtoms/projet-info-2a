To display class diagrams, install "Markdown Preview Mermaid Support" then press ctrl + shift + v

# Card Search Service

Semantic search service for Magic: The Gathering cards using PostgreSQL, pgvector, and embeddings.

---

## 🚀 Quick Start

```bash
# 1. Set up environment variables (see below)
# 2. Initialize database (with embeddings included)
python reset_all_the_database.py
# 3. Start the application
python src/app.py
```

That's it! 🎉

---

## 📋 Prerequisites

### 1. Python 3.10+

Check your version:
```bash
python --version
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. PostgreSQL Service

You need access to a PostgreSQL instance with:
- `pgvector` extension available (configured automatically)
- Permissions to create schemas and tables

### 3. API Token for Embeddings

A token is required to access the embedding API (SSPCloud).

### 4. Environment Variables

Create a `.env` file at the root of the project:

```bash
# API Token for embedding generation
API_TOKEN=your_token_here

# PostgreSQL Configuration
POSTGRES_HOST=your_host
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_SCHEMA=project
```

**Important:** The `.env` file is already in `.gitignore` to protect your credentials.

---

## 📥 Database Setup

### Option 1: Quick Setup with Embeddings (Recommended)

Import cards with pre-computed embeddings:

```bash
python reset_all_the_database.py
```

**What happens:**
- ✅ Database schema initialized
- ✅ ~27,000 cards imported with embeddings
- ✅ pgvector configured automatically
- ✅ Ready for semantic search
- ⏱️ Time: ~2 minutes

### Option 2: Import without Embeddings

If you want to compute embeddings yourself:

```bash
# Import cards without embeddings
python reset_all_the_database.py --no-embeddings

# Compute embeddings (takes 2-4 hours)
python src/technical_components/embedding/compute_all_embeddings.py
```

---

## 🎮 Usage

### Start the API

```bash
python src/app.py
```

The API will be available at: `http://localhost:9876/docs`

### Semantic Search Example

```python
from service.card_service import CardService

# Search for cards
results = CardService().semantic_search("flying dragon", top_k=5)

# Display results
for card in results:
    print(f"{card['name']} - Similarity: {card['similarity']:.3f}")
```

### CLI Interface

```bash
python src/main.py
```

Interactive menu to:
- Search cards by name
- Random card
- Semantic search
- And more...

---

## 🛠️ Additional Tools

### Export Database to JSON

Backup your database with embeddings:

```bash
python export_cards_to_json.py
```

Creates `data/AtomicCardsWithEmbeddings.json`

### Reset Database

⚠️ **Warning:** This will drop all existing data!

```bash
python reset_all_the_database.py
```

---

## 📁 Project Structure

```
projet-info-2a/
├── data/
│   └── init_db.sql              # Database schema
├── src/
│   ├── app.py                   # FastAPI application
│   ├── main.py                  # CLI interface
│   ├── business_object/         # Data models
│   ├── dao/                     # Database access
│   ├── service/                 # Business logic
│   ├── views/                   # CLI views
│   ├── utils/                   # Utilities
│   │   └── reset_all_the_database.py
│   └── technical_components/
│       └── embedding/           # Embedding generation
├── .env                         # Environment variables (create this)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🧪 Testing

Run tests:

```bash
pytest src/tests/
```

---

## 📚 API Documentation

Once the API is running, access the interactive documentation:

```
http://localhost:9876/docs
```

### Available Endpoints

- `POST /find_corresponding_text/` - Semantic search
- More endpoints coming soon...

---

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `API_TOKEN` | Token for embedding API | `your_token_here` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DATABASE` | Database name | `magic_cards` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `your_password` |
| `POSTGRES_SCHEMA` | Schema name | `project` |

---

## 🐛 Troubleshooting

### Database Connection Error

Check your `.env` file and ensure PostgreSQL is running:

```bash
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE
```

### pgvector Extension Not Found

The extension is configured automatically by `reset_all_the_database.py`.
If issues persist, run manually:

```bash
python src/utils/setup_pgvector.py
```

### API Token Invalid

Verify your `API_TOKEN` in the `.env` file is valid.

---

## 📝 Notes

- The **`API_TOKEN`** is required for embedding generation
- `reset_all_the_database.py` will **drop and recreate** the entire schema
- Pre-computed embeddings are included by default (no need to compute them)
- The database uses `pgvector` for efficient semantic search

---

## 🤝 Contributing

See documentation in `doc/` folder for:
- Class diagrams
- Sequence diagrams
- ER diagrams
- Use case diagrams

---

## 📄 License

[Your License Here]