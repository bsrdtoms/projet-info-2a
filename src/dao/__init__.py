import json
import pandas as pd
import requests
from dao.db_connection import DBConnection
from dotenv import load_dotenv


# Charge les variables depuis .env
load_dotenv()


def get_cards_from_url(url: str) -> pd.DataFrame:
    """
    Récupère les cartes depuis un fichier JSON en ligne et retourne un DataFrame.
    """
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Flatten la structure : { "data": { "NomCarte": [ {...}, {...} ] } }
    cards = []
    for name, versions in data["data"].items():
        for card in versions:
            cards.append(card)

    df = pd.DataFrame(cards)
    return df


def insert_all_cards(url: str):
    """
    Récupère toutes les cartes depuis un JSON en ligne et les insère dans la base de données.
    """
    df = get_cards_from_url(url)

    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            for _, row in df.iterrows():
                try:
                    # Convertir les listes/dicts en JSON string
                    colors = json.dumps(row.get("colors", []))
                    color_identity = json.dumps(row.get("colorIdentity", []))
                    identifiers = json.dumps(row.get("identifiers", {}))
                    purchase_urls = json.dumps(row.get("purchaseUrls", {}))
                    foreign_data = json.dumps(row.get("foreignData", []))
                    legalities = json.dumps(row.get("legalities", {}))
                    rulings = json.dumps(row.get("rulings", []))
                    embedding_of_text = json.dumps(row.get("embedding_of_text", []))
                    printings = json.dumps(row.get("printings", []))

                    cursor.execute(
                        """
                        INSERT INTO cards (
                            name, type, mana_cost, mana_value, layout, text,
                            colors, color_identity, first_printing, printings,
                            is_funny, power, toughness, loyalty,
                            identifiers, purchase_urls, foreign_data, legalities, rulings,
                            embedding_of_text
                        )
                        VALUES (%s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s)
                        """,
                        (
                            row.get("name"),
                            row.get("type"),
                            row.get("manaCost"),
                            row.get("manaValue"),
                            row.get("layout"),
                            row.get("text"),
                            colors,
                            color_identity,
                            row.get("firstPrinting"),
                            printings,
                            row.get("isFunny"),
                            row.get("power"),
                            row.get("toughness"),
                            row.get("loyalty"),
                            identifiers,
                            purchase_urls,
                            foreign_data,
                            legalities,
                            rulings,
                            embedding_of_text
                        ),
                    )
                except Exception as e:
                    print(f"Erreur insertion {row.get('name')}: {e}")

        connection.commit()
    print("Toutes les cartes ont été insérées avec succès !")


# Exemple d’utilisation
if __name__ == "__main__":
    url = "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json"
    insert_all_cards(url)
