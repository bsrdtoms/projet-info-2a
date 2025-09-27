import json
from dao.db_connection import DBConnection


def insert_one_card(card: dict):
    """
    Insère une seule carte dans la table 'cards'.
    """
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            try:
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
                        card.get("name"),
                        card.get("type"),
                        card.get("manaCost"),
                        card.get("manaValue"),
                        card.get("layout"),
                        card.get("text"),
                        json.dumps(card.get("colors", [])),
                        json.dumps(card.get("colorIdentity", [])),
                        card.get("firstPrinting"),
                        json.dumps(card.get("printings", [])),
                        card.get("isFunny"),
                        card.get("power"),
                        card.get("toughness"),
                        card.get("loyalty"),
                        json.dumps(card.get("identifiers", {})),
                        json.dumps(card.get("purchaseUrls", {})),
                        json.dumps(card.get("foreignData", [])),
                        json.dumps(card.get("legalities", {})),
                        json.dumps(card.get("rulings", [])),
                        None  # pas d'embedding ici
                    ),
                )
                print(f"✅ Carte '{card.get('name')}' insérée avec succès !")
            except Exception as e:
                print(f"❌ Erreur lors de l'insertion : {e}")

        connection.commit()


if __name__ == "__main__":
    card_json = {
        "colorIdentity": ["G", "R"],
        "colors": ["G", "R"],
        "convertedManaCost": 6.0,
        "firstPrinting": "UNH",
        "foreignData": [],
        "identifiers": {"scryfallOracleId": "a2c5ee76-6084-413c-bb70-45490d818374"},
        "isFunny": True,
        "layout": "normal",
        "legalities": {},
        "manaCost": "{2}{R}{R}{G}{G}",
        "manaValue": 6.0,
        "name": "\"Ach! Hans, Run!\"",
        "printings": ["UNH"],
        "purchaseUrls": {
            "cardKingdom": "https://mtgjson.com/links/84dfefe718a51cf8",
            "cardKingdomFoil": "https://mtgjson.com/links/d8c9f3fc1e93c89c",
            "cardmarket": "https://mtgjson.com/links/b9d69f0d1a9fb80c",
            "tcgplayer": "https://mtgjson.com/links/c51d2b13ff76f1f0"
        },
        "subtypes": [],
        "supertypes": [],
        "text": "At the beginning of your upkeep, you may say \"Ach! Hans, run! It's the . . .\" "
                "and the name of a creature card. If you do, search your library for a card "
                "with that name, put it onto the battlefield, then shuffle. That creature gains haste. "
                "Exile it at the beginning of the next end step.",
        "type": "Enchantment",
        "types": ["Enchantment"]
    }

    insert_one_card(card_json)
