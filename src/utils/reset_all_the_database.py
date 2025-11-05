"""à revoir"""

import json
import requests
from utils.singleton import Singleton
from utils.sql_helpers import sql_value_string
from dao.db_connection import DBConnection


class ResetDatabase(metaclass=Singleton):
    """
    Reset the database and insert cards from the AtomicCards JSON
    """

    def run_sql_string_sql(self, sql_code: str) -> bool:
        """Execute a raw SQL string on the database"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_code)
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            raise
        return True

    def generate_insert_sql_many(self, cards: list[dict]) -> str:
        """Build a single INSERT INTO project.cards statement for many cards"""

        # Columns in the SQL table (order matters)
        columns = [
            "name",
            "ascii_name",
            "type",
            "types",
            "subtypes",
            "supertypes",
            "mana_cost",
            "mana_value",
            "converted_mana_cost",
            "layout",
            "text",
            "colors",
            "color_identity",
            "color_indicator",
            "first_printing",
            "printings",
            "is_funny",
            "is_game_changer",
            "is_reserved",
            "keywords",
            "power",
            "toughness",
            "defense",
            "loyalty",
            "hand",
            "life",
            "side",
            "subsets",
            "attraction_lights",
            "face_converted_mana_cost",
            "face_mana_value",
            "face_name",
            "edhrec_rank",
            "edhrec_saltiness",
            "has_alternative_deck_limit",
            "identifiers",
            "purchase_urls",
            "foreign_data",
            "legalities",
            "rulings",
            "related_cards",
            "leadership_skills",
            "embedding_of_text",
        ]

        # Map JSON keys → SQL column names when different
        key_map = {
            "ascii_name": "asciiName",
            "mana_cost": "manaCost",
            "mana_value": "manaValue",
            "converted_mana_cost": "convertedManaCost",
            "color_identity": "colorIdentity",
            "color_indicator": "colorIndicator",
            "first_printing": "firstPrinting",
            "is_funny": "isFunny",
            "is_game_changer": "isGameChanger",
            "is_reserved": "isReserved",
            "attraction_lights": "attractionLights",
            "face_converted_mana_cost": "faceConvertedManaCost",
            "face_mana_value": "faceManaValue",
            "face_name": "faceName",
            "edhrec_rank": "edhrecRank",
            "edhrec_saltiness": "edhrecSaltiness",
            "has_alternative_deck_limit": "hasAlternativeDeckLimit",
            "purchase_urls": "purchaseUrls",
            "foreign_data": "foreignData",
            "related_cards": "relatedCards",
            "leadership_skills": "leadershipSkills",
            "embedding_of_text": "embedding_of_text",  # same name, just explicit
        }

        all_values = []
        for card in cards:
            values = []
            for col in columns:
                key = key_map.get(col, col)  # map to JSON key if needed
                values.append(sql_value_string(card.get(key)))
            all_values.append(f"({', '.join(values)})")

        sql = (
            f"INSERT INTO project.cards (\n"
            f"    {', '.join(columns)}\n"
            f") VALUES\n"
            f"{',\n'.join(all_values)}\n"
            f";"
        )
        return sql

    def launch(self):
        print("🚀 Resetting database")

        # 1. Run initialization SQL script
        with open("data/init_db.sql", encoding="utf-8") as f:
            init_db_as_string = f.read()
        self.run_sql_string_sql(init_db_as_string)
        print("✅ Database initialized")

        # 2. Load cards from the JSON URL
        url = "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"📦 Found {len(data['data'].keys())} cards")

        # 3. Build one big INSERT for all cards
        all_cards = [versions[0] for _, versions in data["data"].items()]
        sql_string = self.generate_insert_sql_many(all_cards)

        try:
            self.run_sql_string_sql(sql_string)
            print("✅ All cards inserted in one big query")
        except Exception as e:
            print(f"❌ Could not insert all cards: {e}")


# Example usage
if __name__ == "__main__":
    ResetDatabase().launch()
