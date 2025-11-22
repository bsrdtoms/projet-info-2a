# 🎴 MagicSearch - Semantic Search API for Magic: The Gathering Cards

> FastAPI application with vector semantic search using PostgreSQL + pgvector

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.5+-orange.svg)](https://github.com/pgvector/pgvector)

---

## 📋 Quick Start
```bash
# 1. Clone and install
git clone <YOUR_REPO_URL> projet-info-2a
cd projet-info-2a
pip install -r requirements.txt

# 2. Configure .env (see below)

# 3. Initialize database
python src/utils/reset_all_the_database.py

# 4. Start API
python src/app.py
```

API available at: **http://localhost:9876/docs**

---

## 🚀 Setup on Onyxia (SSPCloud)

### 1. Launch PostgreSQL Service

In the [SSPCloud catalog](https://datalab.sspcloud.fr):

1. Select **PostgreSQL** service
2. Choose image: `pgvector/pgvector:pg16` or `ankane/pgvector:latest`
3. Launch service
4. Note connection details from service info panel

### 2. Configure Environment Variables

Create a `.env` file at project root:
```env
# PostgreSQL (from Onyxia service info)
POSTGRES_HOST=postgresql-397117.user-yourname
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=user-yourname
POSTGRES_PASSWORD=your_generated_password
POSTGRES_PORT=5432
POSTGRES_SCHEMA=public

# JWT Authentication
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Embedding API (SSPCloud Ollama)
API_TOKEN=your_sspcloud_api_token
```

**Get your API_TOKEN:**
```bash
# In Onyxia terminal:
echo $MLFLOW_TRACKING_TOKEN
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Initialize Database
```bash
# With pre-computed embeddings (2-3 minutes, recommended)
python src/utils/reset_all_the_database.py

# Without embeddings (if you want to compute them yourself)
python src/utils/reset_all_the_database.py --no-embeddings
python src/technical_components/embedding/compute_all_embeddings.py  # 2-4 hours
```

**What gets created:**
- ✅ ~33,000 Magic cards imported
- ✅ ~32,000 cards with embeddings (some cards have empty text)
- ✅ pgvector extension enabled
- ✅ User tables (`users`, `sessions`, `favorites`, `search_history`)
- ✅ Default admin account created

---

## 🎮 Usage

### Default Admin Account
```
Email: admin@magicsearch.com
Password: our very secure password
```

### API Examples

**1. Register:**
```bash
curl -X POST "http://localhost:9876/user/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
```

**2. Login (get JWT token):**
```bash
curl -X POST "http://localhost:9876/user/login?email=user@example.com&password=pass123"
```

**3. Semantic search:**
```bash
# Public (no auth)
curl -X POST "http://localhost:9876/card/semantic_search_with_L2_distance/?query=flying%20dragon&limit=5"

# Authenticated (saves to history)
curl -X POST "http://localhost:9876/card/semantic_search_with_L2_distance/?query=destroy%20creature&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**4. Manage favorites:**
```bash
# Add to favorites
curl -X POST "http://localhost:9876/favorites/12345" \
  -H "Authorization: Bearer YOUR_TOKEN"

# List favorites
curl -X GET "http://localhost:9876/favorites/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### CLI Interface
```bash
python src/main.py
```

---

## 🏗️ Architecture
```
┌─────────────────────────────┐
│   Presentation Layer        │
│   (FastAPI / CLI)           │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│   Service Layer             │
│   (Business Logic)          │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│   DAO Layer                 │
│   (Data Access)             │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│   PostgreSQL + pgvector     │
└─────────────────────────────┘
```

**Project Structure:**
```
src/
├── app.py                    # FastAPI application
├── main.py                   # CLI interface
├── business_object/          # Domain models
├── dao/                      # Database access
├── service/                  # Business logic
├── views/                    # CLI views
├── utils/                    # Utilities
└── technical_components/     # Embeddings API
```

---

## 📚 API Endpoints

### Public (no authentication)
- `GET /card/random` - Random card
- `GET /card/name/{name}` - Search by name
- `POST /card/semantic_search_with_L2_distance/` - Semantic search (L2)
- `POST /card/semantic_search_with_cosine_distance/` - Semantic search (cosine)
- `POST /user/register` - Create account (client role)
- `POST /user/login` - Login and get JWT token

### Authenticated
- `GET /user/me` - My profile
- `POST /favorites/{card_id}` - Add to favorites
- `DELETE /favorites/{card_id}` - Remove from favorites
- `GET /favorites/` - List my favorites
- `GET /history` - My search history
- `DELETE /history` - Clear history

### Game Designer Role
- `POST /card/{name}/{text}` - Create card
- `PUT /card/{card_id}` - Update card
- `DELETE /card/{card_id}` - Delete card

### Admin Role
- `GET /user/` - List all users
- `POST /admin/user/` - Create user (any role)
- `PUT /admin/user/{user_id}` - Update user
- `DELETE /admin/{user_id}` - Delete user
- `GET /admin/stats` - Global statistics

**Interactive documentation:** http://localhost:9876/docs

---

## 🧪 Tests
```bash
# Run all tests
pytest src/tests/

# With coverage
pytest src/tests/ --cov=src --cov-report=html

# Test authentication system
python src/tests/test_authentication.py
```

---

## 🔧 Troubleshooting

### Connection refused to PostgreSQL
```bash
# Check service is running in Onyxia "My Services"
# Test connection
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE -c "SELECT 1"
```

### pgvector extension not found
```bash
# Ensure you used pgvector/pgvector:pg16 image
# Manually enable if needed:
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DATABASE -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Invalid API_TOKEN
```bash
# Test token manually
curl -X POST "https://llm.lab.sspcloud.fr/ollama/api/embed" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model":"bge-m3:latest","input":"test"}'
```

### Port already in use
```bash
# Find process
lsof -i :9876

# Kill it
kill -9 <PID>

# Or use different port
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

---

## 📊 Database Stats

After initialization:
- **Total cards:** ~33,000
- **Cards with embeddings:** ~32,000 (cards without text are skipped)
- **Embedding dimension:** 1024 (bge-m3 model)
- **Database size:** ~500 MB with embeddings

Check your database:
```bash
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DATABASE

-- Count cards
SELECT COUNT(*) FROM public.cards;

-- Count embeddings
SELECT COUNT(*) FROM public.cards WHERE embedding_of_text IS NOT NULL;

-- Sample semantic search
SELECT name, text 
FROM public.cards 
WHERE embedding_of_text IS NOT NULL 
ORDER BY embedding_of_text <-> '[0.1, 0.2, ...]'::vector 
LIMIT 5;
```

---

## 📖 Resources

- **Onyxia Documentation:** https://datalab.sspcloud.fr/
- **PostgreSQL pgvector:** https://github.com/pgvector/pgvector
- **FastAPI Documentation:** https://fastapi.tiangolo.com/

