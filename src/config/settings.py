import os

# URL of the JSON with all cards
CARDS_JSON_URL = os.getenv(
    "CARDS_JSON_URL", "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json"
)

# SQL initialization file
INIT_DB_FILE = os.getenv("INIT_DB_FILE", "data/init_db.sql")
