import json

# Chemins
json_file = "data/AtomicCards.json"
sql_file = "data/pop_db.sql"

# Charger les cartes
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
    
cards = data["data"]   # Récupérer seulement la liste des cartes


# Colonnes
colonnes = [
    'name', 'asciiName', 'type', 'text', 'manaCost', 'manaValue',
    'convertedManaCost', 'faceName', 'faceManaValue',
    'faceConvertedManaCost', 'side', 'colorIdentity', 'colors',
    'colorIndicator', 'subtypes', 'supertypes', 'types', 'keywords',
    'firstPrinting', 'printings', 'foreignData', 'identifiers',
    'purchaseUrls', 'rulings', 'legalities', 'leadershipSkills',
    'layout', 'isFunny', 'isReserved', 'hasAlternativeDeckLimit',
    'edhrecRank', 'edhrecSaltiness', 'power', 'toughness',
    'loyalty', 'hand', 'life', 'defense'
]

# Colonnes à stocker en JSON
colonnes_json = {
    "colorIdentity", "colors", "colorIndicator", "subtypes", "supertypes",
    "types", "keywords", "printings", "foreignData", "identifiers",
    "purchaseUrls", "rulings", "legalities", "leadershipSkills"
}

with open(sql_file, "w", encoding="utf-8") as f:
    f.write("-- pop_db.sql généré automatiquement\n")

    for card in cards:
        valeurs = []
        for col in colonnes:
            if isinstance(card, dict):
                val = card.get(col, None)
            else:
                val = None
            if val is None:
                valeurs.append("NULL")
            elif col in colonnes_json:
                # Sérialiser en JSON, échapper les apostrophes simples
                val_json = json.dumps(val).replace("'", "''")
                valeurs.append(f"'{val_json}'::jsonb")
            elif isinstance(val, str):
                # Échapper les apostrophes simples
                val_str = val.replace("'", "''")
                valeurs.append(f"'{val_str}'")
            else:
                valeurs.append(str(val))

        colonnes_str = ", ".join(colonnes)
        valeurs_str = ", ".join(valeurs)
        f.write(f"INSERT INTO cards ({colonnes_str}) VALUES ({valeurs_str});\n")

print(f"Fichier {sql_file} généré avec {len(cards)} cartes.")
