import json
import requests
from utils.singleton import Singleton
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

    def sql_value_string(self, value):
        """Convert a Python value to a SQL literal string"""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            if len(value) == 0:
                return "'{}'"
            # If it's a list of dicts → JSONB
            if all(isinstance(el, dict) for el in value):
                return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
            # Otherwise → PostgreSQL array
            elems = []
            for el in value:
                if isinstance(el, (int, float)):
                    elems.append(str(el))
                else:
                    # Escape single quotes and double quotes
                    safe = str(el).replace("'", "''").replace('"', '\\"')
                    elems.append(f'"{safe}"')
            return "'{" + ",".join(elems) + "}'"
        elif isinstance(value, dict):
            return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
        else:
            # Escape single quotes in plain text
            return "'" + str(value).replace("'", "''") + "'"

    def generate_insert_sql_many(self, cards: list[dict]) -> str:
        """Build a single INSERT INTO project.cards statement for many cards"""

        # Match all columns of project.cards
        columns = [
            "name", "ascii_name", "type", "types", "subtypes", "supertypes",
            "mana_cost", "mana_value", "converted_mana_cost", "layout", "text",
            "colors", "color_identity", "color_indicator",
            "first_printing", "printings",
            "is_funny", "is_game_changer", "is_reserved",
            "keywords", "power", "toughness", "defense", "loyalty",
            "hand", "life", "side", "subsets",
            "attraction_lights", "face_converted_mana_cost", "face_mana_value", "face_name",
            "edhrec_rank", "edhrec_saltiness", "has_alternative_deck_limit",
            "identifiers", "purchase_urls", "foreign_data", "legalities", "rulings",
            "related_cards", "leadership_skills", "embedding_of_text"
        ]
        f"<SE {}"

        all_values = []
        for card in cards:
            values = [
                self.sql_value_string(card.get("name")),
                self.sql_value_string(card.get("asciiName")),
                self.sql_value_string(card.get("type")),
                self.sql_value_string(card.get("types", [])),
                self.sql_value_string(card.get("subtypes", [])),
                self.sql_value_string(card.get("supertypes", [])),
                self.sql_value_string(card.get("manaCost")),
                self.sql_value_string(card.get("manaValue")),
                self.sql_value_string(card.get("convertedManaCost")),
                self.sql_value_string(card.get("layout")),
                self.sql_value_string(card.get("text")),
                self.sql_value_string(card.get("colors", [])),
                self.sql_value_string(card.get("colorIdentity", [])),
                self.sql_value_string(card.get("colorIndicator", [])),
                self.sql_value_string(card.get("firstPrinting")),
                self.sql_value_string(card.get("printings", [])),
                self.sql_value_string(card.get("isFunny")),
                self.sql_value_string(card.get("isGameChanger")),
                self.sql_value_string(card.get("isReserved")),
                self.sql_value_string(card.get("keywords", [])),
                self.sql_value_string(card.get("power")),
                self.sql_value_string(card.get("toughness")),
                self.sql_value_string(card.get("defense")),
                self.sql_value_string(card.get("loyalty")),
                self.sql_value_string(card.get("hand")),
                self.sql_value_string(card.get("life")),
                self.sql_value_string(card.get("side")),
                self.sql_value_string(card.get("subsets", [])),
                self.sql_value_string(card.get("attractionLights", [])),
                self.sql_value_string(card.get("faceConvertedManaCost")),
                self.sql_value_string(card.get("faceManaValue")),
                self.sql_value_string(card.get("faceName")),
                self.sql_value_string(card.get("edhrecRank")),
                self.sql_value_string(card.get("edhrecSaltiness")),
                self.sql_value_string(card.get("hasAlternativeDeckLimit")),
                self.sql_value_string(card.get("identifiers", {})),
                self.sql_value_string(card.get("purchaseUrls", {})),
                self.sql_value_string(card.get("foreignData", [])),
                self.sql_value_string(card.get("legalities", {})),
                self.sql_value_string(card.get("rulings", [])),
                self.sql_value_string(card.get("relatedCards", {})),
                self.sql_value_string(card.get("leadershipSkills", {})),
                self.sql_value_string(card.get("embedding_of_text"))
            ]
            all_values.append(f"({', '.join(values)})")

        sql = f"""INSERT INTO project.cards (
    {", ".join(columns)}
) VALUES
{",\n".join(all_values)}
;"""
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
