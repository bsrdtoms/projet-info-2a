import os

# URL du JSON avec toutes les cartes
CARDS_JSON_URL = os.getenv("CARDS_JSON_URL", "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json")

# Fichier SQL d'init
INIT_DB_FILE = os.getenv("INIT_DB_FILE", "data/init_db.sql")
