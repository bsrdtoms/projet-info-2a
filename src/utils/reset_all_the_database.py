"""
Reset the database and insert cards from JSON
Two modes:
1. Default: download from URL AtomicCardsWithEmbeddings.json (WITH embeddings)
2. With parameter: download from URL AtomicCards.json (WITHOUT embeddings)

Usage:
    python reset_all_the_database.py                    # Default: with embeddings from URL
    python reset_all_the_database.py --no-embeddings    # From URL without embeddings
"""
import requests
import argparse
from utils.singleton import Singleton
from utils.sql_helpers import sql_value_string
from dao.db_connection import DBConnection
from utils.setup_pgvector import PgVectorSetup
import utils.init_users_tables


class ResetDatabase(metaclass=Singleton):
    """
    Reset the database and insert cards from JSON
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

    def generate_insert_sql_many(
        self, cards: list[dict], with_embeddings: bool = True
    ) -> str:
        """
        Build a single INSERT INTO project.cards statement for many cards

        Parameters
        ----------
        cards : list[dict]
            List of card dictionaries
        with_embeddings : bool
            If True, include embedding_of_text column
        """

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
        ]

        if with_embeddings:
            columns.append("embedding_of_text")

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
            "embedding_of_text": "embedding_of_text",
        }

        all_values = []
        for card in cards:
            values = []
            for col in columns:
                key = key_map.get(col, col)  # map to JSON key if needed

                # Special handling for embeddings
                if col == "embedding_of_text" and key in card:
                    embedding = card[key]
                    if embedding is not None and isinstance(embedding, list):
                        # Convert list to pgvector format: [0.1,0.2,0.3]
                        embedding_str = "[" + ",".join(str(f) for f in embedding) + "]"
                        values.append(f"'{embedding_str}'::vector")
                    else:
                        values.append("NULL")
                else:
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

    def launch(self, use_embeddings: bool = True, add_all_cards: bool = True):
        """
        Reset database and import cards

        Parameters
        ----------
        use_embeddings : bool
            If True (default), download AtomicCardsWithEmbeddings.json WITH embeddings
            If False, download AtomicCards.json WITHOUT embeddings
        """

        print("🚀 Resetting database")

        # 1. Run initialization SQL script
        with open("data/init_db.sql", encoding="utf-8") as f:
            init_db_as_string = f.read()
        self.run_sql_string_sql(init_db_as_string)
        print("✅ Database initialized")

        if add_all_cards:
            # 2. Download cards from appropriate URL
            if use_embeddings:
                # Mode 1: Download WITH embeddings
                url = (
                    "https://minio.lab.sspcloud.fr/thomasfr/AtomicCardsWithEmbeddings.json"
                )
                print(f"📦 Downloading cards from {url} (WITH embeddings ✨)")
                with_embeddings = True
            else:
                # Mode 2: Download WITHOUT embeddings
                url = "https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json"
                print(f"📦 Downloading cards from {url} (WITHOUT embeddings)")
                with_embeddings = False
    
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"❌ Error downloading from {url}: {e}")
                return False
    
            print(f"📊 Found {len(data['data'].keys())} unique card names")
    
            # 3. Build one big INSERT for all cards (first version of each card)
            all_cards = [versions[0] for _, versions in data["data"].items()]
    
            print(f"💾 Preparing to insert {len(all_cards)} cards...")
            sql_string = self.generate_insert_sql_many(
                all_cards, with_embeddings=with_embeddings
            )
    
            try:
                self.run_sql_string_sql(sql_string)
                embeddings_status = (
                    "WITH embeddings ✨" if with_embeddings else "WITHOUT embeddings"
                )
                print(f"✅ All {len(all_cards)} cards inserted {embeddings_status}")
                return True
            except Exception as e:
                print(f"❌ Could not insert all cards: {e}")
                return False


def main(add_all_cards: bool = True):
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Reset database and import Magic cards from URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reset_all_the_database.py                  # Default: download with embeddings
  python reset_all_the_database.py --no-embeddings  # Download without embeddings

URLs used:
  - With embeddings: https://minio.lab.sspcloud.fr/thomasfr/AtomicCardsWithEmbeddings.json
  - Without embeddings: https://minio.lab.sspcloud.fr/thomasfr/AtomicCards.json
        """,
    )

    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Download AtomicCards.json (without embeddings) instead of AtomicCardsWithEmbeddings.json",
    )

    args = parser.parse_args()

    # Default: download WITH embeddings
    # With --no-embeddings: download WITHOUT embeddings
    use_embeddings = not args.no_embeddings

    # Now we automatically call setup_pgvector.py
    pgvector_setup = PgVectorSetup()
    pgvector_setup.setup()

    ResetDatabase().launch(use_embeddings=use_embeddings, add_all_cards=add_all_cards)
    # Now we automatically call init_user_tables.py
    utils.init_users_tables.main()


if __name__ == "__main__":
    main()
