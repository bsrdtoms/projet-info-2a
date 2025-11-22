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

# 4. Start CLI
python src/main.py

# 4. Or start API
python src/app.py

```

API available at: **http://localhost:9876/docs**

---

## 🚀 Setup on Onyxia (SSPCloud)

### 1. Launch PostgreSQL Service

In the [SSPCloud catalog](https://datalab.sspcloud.fr):

1. Select **PostgreSQL** service
2. Choose image: `inseefrlab/onyxia-postgresql-pgvector` reather than the default `bitnamilegacy/postgresql`
3. Launch service
4. Note connection details from service info panel

### 2. Launch VSCode Service
1. Open the port 9876 so that the API has a port to run on.
2. run on a termial :
```bash
git clone <YOUR_REPO_URL> projet-info-2a
cd projet-info-2a
export PYTHONPATH=/home/onyxia/work/projet-info-2a/src
pip install -r ~/work/projet-info-2a/requirements.txt
```
3. Configure Environment Variables

Create a `.env` file at project root (in the folder projet-info-2a):
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


### 3. Initialize Database
```bash
# With pre-computed embeddings (1 minute, recommended)
python src/utils/reset_all_the_database.py

# Without embeddings (if you want to compute them yourself)
python src/utils/reset_all_the_database.py --no-embeddings
python src/technical_components/embedding/compute_all_embeddings.py  # 1/2 hours
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

# Test authentication system
python src/tests/test_authentication.py
```

---

## 📊 Database Stats

After initialization:
- **Total cards:** ~33,000
- **Cards with embeddings:** ~32,000 (cards without text are skipped)
- **Embedding dimension:** 1024 (bge-m3 model)
- **Database size:** ~500 MB with embeddings

