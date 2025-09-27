'''import json
import requests
from utils.singleton import Singleton
from dao.db_connection import DBConnection


class ResetDatabase(metaclass=Singleton):
    """
    Reinitialisation de la base de données
    """

    def run_sql_string_sql(self, sql_code):
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_code)
        except Exception as e:
            print(e)
            raise

        return True

    def sql_value_string(self, value):
        """Convert a Python value to a SQL literal string."""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            # PostgreSQL array literal for TEXT[]
            return "{" + ",".join(str(v) for v in value) + "}"
        elif isinstance(value, dict):
            # JSONB field
            return "'" + json.dumps(value).replace("'", "''") + "'"
        else:
            # Text: escape single quotes
            return "'" + str(value).replace("'", "''") + "'"

    def generate_insert_sql(self, card):
        columns = [
            "name", "type", "mana_cost", "mana_value", "layout", "text",
            "colors", "color_identity", "first_printing", "printings",
            "is_funny", "power", "toughness", "loyalty",
            "identifiers", "purchase_urls", "foreign_data", "legalities", "rulings",
            "embedding_of_text"
        ]

        values = [
            self.sql_value_string(card.get("name")),
            self.sql_value_string(card.get("type")),
            self.sql_value_string(card.get("manaCost")),
            self.sql_value_string(card.get("manaValue")),
            self.sql_value_string(card.get("layout")),
            self.sql_value_string(card.get("text")),
            self.sql_value_string(card.get("colors", [])),
            self.sql_value_string(card.get("colorIdentity", [])),
            self.sql_value_string(card.get("firstPrinting")),
            self.sql_value_string(card.get("printings", [])),
            self.sql_value_string(card.get("isFunny")),
            self.sql_value_string(card.get("power")),
            self.sql_value_string(card.get("toughness")),
            self.sql_value_string(card.get("loyalty")),
            self.sql_value_string(card.get("identifiers", {})),
            self.sql_value_string(card.get("purchaseUrls", {})),
            self.sql_value_string(card.get("foreignData", [])),
            self.sql_value_string(card.get("legalities", {})),
            self.sql_value_string(card.get("rulings", [])),
            self.sql_value_string(card.get("embedding_of_text"))
        ]

        sql = f"INSERT INTO project.cards (\n    {', '.join(columns)}\n) VALUES (\n    {',\n    '.join(values)}\n);"
        return sql

    def launch(self):
        print("Ré-initialisation de la base de données")
        init_db = open("data/init_db.sql", encoding="utf-8")
        init_db_as_string = init_db.read()
        self.run_sql_string_sql(init_db_as_string)
        print("fin init")

        # Charge une carte depuis une URL JSON
        url = "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json"
        response = requests.get(url)
        response.raise_for_status()  # lève une erreur si le téléchargement échoue

        data = response.json()

        # Exemple : prendre la première carte
        card_name, versions = list(data["data"].items())[0]
        card = versions[0]

        # Ici tu peux utiliser generate_insert_sql(card) comme avant
        sql_string = self.generate_insert_sql(card)
        print(sql_string)
        self.run_sql_string_sql(sql_string)


# Exemple d'utilisation
if __name__ == "__main__":
    ResetDatabase().launch()
''


# english code - french explanation above
import json
import requests
from typing import Any, List, Optional

def sql_escape(s: str) -> str:
    """Escape single quotes for SQL string literals."""
    return s.replace("'", "''")

def to_sql_text(value: Optional[Any]) -> str:
    if value is None:
        return "NULL"
    return f"'{sql_escape(str(value))}'"

def to_sql_bool(value: Optional[bool]) -> str:
    if value is None:
        return "NULL"
    return "TRUE" if bool(value) else "FALSE"

def to_sql_number(value: Optional[Any]) -> str:
    if value is None:
        return "NULL"
    # Keep floats/ints as-is
    return str(value)

def to_sql_text_array(lst: Optional[List[Any]]) -> str:
    """
    Produce a PostgreSQL array literal as a SQL string literal.
    Example: ['G','R'] -> '{"G","R"}'  (and wrapped as a SQL string: '\{"G","R"\}')
    """
    if lst is None:
        return "NULL"
    if not isinstance(lst, (list, tuple)):
        return "NULL"
    if len(lst) == 0:
        # empty array literal
        return "'{}'"
    elems = []
    for el in lst:
        el_str = str(el)
        # escape backslashes and double quotes inside element, to be safe
        el_str = el_str.replace('\\', '\\\\').replace('"', '\\"')
        elems.append(f'"{el_str}"')
    array_literal = "{" + ",".join(elems) + "}"
    return f"'{array_literal}'"

def to_sql_float_array(lst: Optional[List[float]]) -> str:
    """
    Produce a PostgreSQL float array literal as a SQL string literal,
    or NULL if missing/empty.
    """
    if lst is None:
        return "NULL"
    if not isinstance(lst, (list, tuple)) or len(lst) == 0:
        return "NULL"
    # Format floats nicely
    items = []
    for x in lst:
        try:
            # ensure numeric formatting
            items.append(repr(float(x)))
        except Exception:
            # fallback to 0.0 if weird
            items.append("0.0")
    array_literal = "{" + ",".join(items) + "}"
    return f"'{array_literal}'"

def to_sql_jsonb(obj: Optional[Any]) -> str:
    """Serialize to JSON and wrap as a SQL single-quoted literal (JSONB column)."""
    if obj is None:
        return "NULL"
    text = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    text = sql_escape(text)
    return f"'{text}'"

def generate_insert_sql(card: dict) -> str:
    """
    Generate an INSERT statement for table project.cards for a single card dict.
    Column order matches:
    name, type, mana_cost, mana_value, layout, text,
    colors, color_identity, first_printing, printings,
    is_funny, power, toughness, loyalty,
    identifiers, purchase_urls, foreign_data, legalities, rulings,
    embedding_of_text
    """
    cols = [
        "name", "type", "mana_cost", "mana_value", "layout", "text",
        "colors", "color_identity", "first_printing", "printings",
        "is_funny", "power", "toughness", "loyalty",
        "identifiers", "purchase_urls", "foreign_data", "legalities", "rulings",
        "embedding_of_text"
    ]

    values = [
        to_sql_text(card.get("name")),
        to_sql_text(card.get("type")),
        to_sql_text(card.get("manaCost")),
        to_sql_number(card.get("manaValue")),
        to_sql_text(card.get("layout")),
        to_sql_text(card.get("text")),
        to_sql_text_array(card.get("colors", [])),
        to_sql_text_array(card.get("colorIdentity", [])),
        to_sql_text(card.get("firstPrinting")),
        to_sql_text_array(card.get("printings", [])),
        to_sql_bool(card.get("isFunny")),
        to_sql_text(card.get("power")),
        to_sql_text(card.get("toughness")),
        to_sql_text(card.get("loyalty")),
        to_sql_jsonb(card.get("identifiers", {})),
        to_sql_jsonb(card.get("purchaseUrls", {})),
        to_sql_jsonb(card.get("foreignData", [])),
        to_sql_jsonb(card.get("legalities", {})),
        to_sql_jsonb(card.get("rulings", [])),
        to_sql_float_array(card.get("embedding_of_text"))
    ]

    # Build pretty multiline SQL string
    cols_sql = ", ".join(cols)
    vals_sql = ",\n    ".join(values)
    sql = (
        "INSERT INTO project.cards (\n"
        f"    {cols_sql}\n"
        ") VALUES (\n"
        f"    {vals_sql}\n"
        ");"
    )
    return sql

def fetch_json(url: str) -> dict:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    # URL with AtomicCards.json
    url = "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json"
    data = fetch_json(url)

    # try exact key first (some card names include surrounding quotes)
    target_name = '"Ach! Hans, Run!"'
    card = None
    if "data" in data and target_name in data["data"]:
        card = data["data"][target_name][0]
    else:
        # fallback: search for an entry that contains the phrase (more lenient)
        for k, versions in data.get("data", {}).items():
            if "Ach! Hans, Run!" in k:
                card = versions[0]
                break

    # fallback to the very first card if nothing found
    if card is None:
        first_group = next(iter(data.get("data", {}).values()))
        card = first_group[0]

    sql_string = generate_insert_sql(card)
    print(sql_string)
''

import json
import requests
from utils.singleton import Singleton
from dao.db_connection import DBConnection


class ResetDatabase(metaclass=Singleton):
    """
    Reset the database and insert cards
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
            # PostgreSQL array literal (TEXT[] or FLOAT[])
            elems = []
            for el in value:
                if isinstance(el, (int, float)):
                    elems.append(str(el))
                else:
                    safe = str(el).replace('"', '\\"')
                    elems.append(f'"{safe}"')
            return "'{" + ",".join(elems) + "}'"
        elif isinstance(value, dict):
            # JSONB field
            return "'" + json.dumps(value).replace("'", "''") + "'"
        else:
            # Text with single-quote escaping
            return "'" + str(value).replace("'", "''") + "'"

    def generate_insert_sql(self, card: dict) -> str:
        """Build the INSERT INTO project.cards SQL statement for one card"""
        columns = [
            "name", "type", "mana_cost", "mana_value", "layout", "text",
            "colors", "color_identity", "first_printing", "printings",
            "is_funny", "power", "toughness", "loyalty",
            "identifiers", "purchase_urls", "foreign_data", "legalities", "rulings",
            "embedding_of_text"
        ]

        values = [
            self.sql_value_string(card.get("name")),
            self.sql_value_string(card.get("type")),
            self.sql_value_string(card.get("manaCost")),
            self.sql_value_string(card.get("manaValue")),
            self.sql_value_string(card.get("layout")),
            self.sql_value_string(card.get("text")),
            self.sql_value_string(card.get("colors", [])),
            self.sql_value_string(card.get("colorIdentity", [])),
            self.sql_value_string(card.get("firstPrinting")),
            self.sql_value_string(card.get("printings", [])),
            self.sql_value_string(card.get("isFunny")),
            self.sql_value_string(card.get("power")),
            self.sql_value_string(card.get("toughness")),
            self.sql_value_string(card.get("loyalty")),
            self.sql_value_string(card.get("identifiers", {})),
            self.sql_value_string(card.get("purchaseUrls", {})),
            self.sql_value_string(card.get("foreignData", [])),
            self.sql_value_string(card.get("legalities", {})),
            self.sql_value_string(card.get("rulings", [])),
            self.sql_value_string(card.get("embedding_of_text"))
        ]

        sql = f"""INSERT INTO project.cards (
    {", ".join(columns)}
) VALUES (
    {",\n    ".join(values)}
);"""
        return sql

    def launch(self):
        print("🚀 Resetting database")

        # 1. Run initialization SQL script
        with open("data/init_db.sql", encoding="utf-8") as f:
            init_db_as_string = f.read()
        self.run_sql_string_sql(init_db_as_string)
        print("✅ Database initialized")

        # 2. Load one card from the JSON URL
        url = "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        all_cards = list(data["data"].items())
        for i in range(len(data["data"])):
            print(200*"_")
            print(all_cards[i])

            # Example: take the first card
            card_name, versions = all_cards[i]
            card = versions[0]
            # 3. Generate SQL and insert the card
            sql_string = self.generate_insert_sql(card)
            self.run_sql_string_sql(sql_string)
        

# Example usage
if __name__ == "__main__":
    ResetDatabase().launch()
'''

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

    '''def sql_value_string(self, value):
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
            # Check if this is a list of dicts → JSONB
            if all(isinstance(el, dict) for el in value):
                return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
            # Otherwise treat as a SQL array
            elems = []
            for el in value:
                if isinstance(el, (int, float)):
                    elems.append(str(el))
                else:
                    safe = str(el).replace('"', '\\"')
                    elems.append(f'"{safe}"')
            return "'{" + ",".join(elems) + "}'"
        elif isinstance(value, dict):
            # JSONB field
            return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
        else:
            # Text with single-quote escaping
            return "'" + str(value).replace("'", "''") + "'" '''
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

    def generate_insert_sql(self, card: dict) -> str:
        """Build the INSERT INTO project.cards SQL statement for one card"""

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

        # Convert each field safely
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

        sql = f"""INSERT INTO project.cards (
    {", ".join(columns)}
) VALUES (
    {",\n    ".join(values)}
);"""
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
        print(len(data["data"].keys()))
        """
        # 3. Iterate through all cards and insert them
        for card_name, versions in data["data"].items():
            card = versions[0]  # take the first version
            sql_string = self.generate_insert_sql(card)
            try:
                self.run_sql_string_sql(sql_string)
            except Exception as e:
                print(f"⚠️ Could not insert card {card_name}: {e}")
        """

# Example usage
if __name__ == "__main__":
    ResetDatabase().launch()
