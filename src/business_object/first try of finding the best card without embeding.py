import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import NearestNeighbors

# --- Chargement des données ---
with open("projet-info-2a/data/AtomicCards.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Certaines cartes ont plusieurs versions → on les met toutes dans une liste
cards = []
for name, versions in data["data"].items():
    for card in versions:
        cards.append(card)

df = pd.DataFrame(cards)


# --- Prétraitement des données ---

# Fonction pour transformer power/toughness en nombres utilisables
def safe_to_numeric(val):
    try:
        return float(val)
    except:
        return None  # on mettra 0 ensuite avec fillna


df["power_num"] = df["power"].apply(safe_to_numeric)
df["toughness_num"] = df["toughness"].apply(safe_to_numeric)

# Encodage des colonnes catégorielles
mlb_colors = MultiLabelBinarizer().fit(df["colors"].dropna().apply(lambda x: x if isinstance(x, list) else []))
colors_encoded = pd.DataFrame(mlb_colors.transform(df["colors"].dropna().apply(lambda x: x if isinstance(x, list) else [])),
                              columns=mlb_colors.classes_, index=df.index)

mlb_types = MultiLabelBinarizer().fit(df["types"].dropna().apply(lambda x: x if isinstance(x, list) else []))
types_encoded = pd.DataFrame(mlb_types.transform(df["types"].dropna().apply(lambda x: x if isinstance(x, list) else [])),
                             columns=mlb_types.classes_, index=df.index)

mlb_subtypes = MultiLabelBinarizer().fit(df["subtypes"].dropna().apply(lambda x: x if isinstance(x, list) else []))
subtypes_encoded = pd.DataFrame(mlb_subtypes.transform(df["subtypes"].dropna().apply(lambda x: x if isinstance(x, list) else [])),
                                columns=mlb_subtypes.classes_, index=df.index)

# Construction du dataset pour le modèle
X = pd.concat(
    [df[["manaValue", "power_num", "toughness_num"]], colors_encoded, types_encoded, subtypes_encoded],
    axis=1
).fillna(0)


# --- Entraînement du modèle kNN ---
knn = NearestNeighbors(n_neighbors=1, metric="euclidean")
knn.fit(X)


# --- Fonction pour trouver la carte la plus proche ---
def find_closest_card(card_data):
    input_df = pd.DataFrame([{
        "manaValue": card_data.get("manaValue", 0),
        "power_num": safe_to_numeric(card_data.get("power", 0)),
        "toughness_num": safe_to_numeric(card_data.get("toughness", 0)),
    }])

    input_colors = pd.DataFrame(mlb_colors.transform([card_data.get("colors", [])]),
                                columns=mlb_colors.classes_)
    input_types = pd.DataFrame(mlb_types.transform([card_data.get("types", [])]),
                               columns=mlb_types.classes_)
    input_subtypes = pd.DataFrame(mlb_subtypes.transform([card_data.get("subtypes", [])]),
                                  columns=mlb_subtypes.classes_)

    input_X = pd.concat([input_df, input_colors, input_types, input_subtypes], axis=1).fillna(0)

    dist, idx = knn.kneighbors(input_X)
    return df.iloc[idx[0][0]]["name"]


# --- Exemple d'utilisation ---
new_card = {
    "colors": ["R", "W"],
    "manaValue": 7,
    "power": 3,
    "toughness": 2,
    "types": ["Creature"],
    "subtypes": ["Human"]
}

print("Carte la plus proche :", find_closest_card(new_card))
