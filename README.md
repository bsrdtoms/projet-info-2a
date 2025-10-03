Pour afficher le diagramme de classe, penser à installer "Markdown Preview Mermaid Support" puis ctrl + shift + v

# Card Search Service

This project provides a service to search and work with Magic: The Gathering cards using PostgreSQL and embeddings.

There are **two ways** to use this repository, depending on whether you already have a PostgreSQL database filled with pre-computed card embeddings or not.

---

## Prerequisites

* Python 3.10+
* A running PostgreSQL service
* Environment variables properly configured

Required environment variables:

```bash
# Token to access the embedding API
export API_TOKEN=your_token_here

# PostgreSQL service configuration
export DB_HOST=your_host
export DB_PORT=5432
export DB_NAME=your_database
export DB_USER=your_user
export DB_PASSWORD=your_password
```

---

## Usage

### 1. If you already have a PostgreSQL service with embedded cards

In this case, you only need to:

```bash
# Make sure your environment variables are set
export API_TOKEN=your_token_here
# Start the application
python app.py
```

---

### 2. If you do **not** have a pre-filled PostgreSQL service

In this case, you must:

1. Set up the environment variables (see [Prerequisites](#prerequisites))

2. Initialize and populate the database schema:

   ```bash
   python reset_all_th_database.py
   ```

3. Compute embeddings for all cards:

   ```bash
   python compute_all_embeddings.py
   ```

4. Finally, start the application:

   ```bash
   python app.py
   ```

---

## Notes

* The **`API_TOKEN`** environment variable must be set in **all cases**, since the embedding service depends on it.
* The PostgreSQL database will contain the card data and their corresponding embeddings.
* If you re-run `reset_all_th_database.py`, your existing database schema and data will be dropped and recreated from scratch.
