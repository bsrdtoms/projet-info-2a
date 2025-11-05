"""
Export all cards from PostgreSQL to JSON format (with embeddings)
Creates data/AtomicCardsWithEmbeddings.json compatible with AtomicCards.json structure
"""

import json
import os
from dao.db_connection import DBConnection


def export_cards_to_json(output_file: str = "data/AtomicCardsWithEmbeddings.json"):
    """
    Export all cards from project.cards to JSON file

    Parameters
    ----------
    output_file : str
        Path to output JSON file (default: data/AtomicCardsWithEmbeddings.json)
    """

    print(f"🚀 Exporting cards from PostgreSQL to {output_file}")

    # SQL query to get all cards with all columns
    sql_query = """
        SELECT
            id,
            name,
            ascii_name,
            type,
            types,
            subtypes,
            supertypes,
            mana_cost,
            mana_value,
            converted_mana_cost,
            layout,
            text,
            colors,
            color_identity,
            color_indicator,
            first_printing,
            printings,
            is_funny,
            is_game_changer,
            is_reserved,
            keywords,
            power,
            toughness,
            defense,
            loyalty,
            hand,
            life,
            side,
            subsets,
            attraction_lights,
            face_converted_mana_cost,
            face_mana_value,
            face_name,
            edhrec_rank,
            edhrec_saltiness,
            has_alternative_deck_limit,
            identifiers,
            purchase_urls,
            foreign_data,
            legalities,
            rulings,
            related_cards,
            leadership_skills,
            embedding_of_text
        FROM project.cards
        ORDER BY name
    """

    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()

        print(f"📦 Found {len(rows)} cards in database")

        # Convert to AtomicCards.json structure: {"data": {"CardName": [versions]}}
        data_dict = {}

        for row in rows:
            # Convert PostgreSQL row to dict matching JSON structure
            card_data = {
                "name": row["name"],
                "asciiName": row["ascii_name"],
                "type": row["type"],
                "types": row["types"],
                "subtypes": row["subtypes"],
                "supertypes": row["supertypes"],
                "manaCost": row["mana_cost"],
                "manaValue": row["mana_value"],
                "convertedManaCost": row["converted_mana_cost"],
                "layout": row["layout"],
                "text": row["text"],
                "colors": row["colors"],
                "colorIdentity": row["color_identity"],
                "colorIndicator": row["color_indicator"],
                "firstPrinting": row["first_printing"],
                "printings": row["printings"],
                "isFunny": row["is_funny"],
                "isGameChanger": row["is_game_changer"],
                "isReserved": row["is_reserved"],
                "keywords": row["keywords"],
                "power": row["power"],
                "toughness": row["toughness"],
                "defense": row["defense"],
                "loyalty": row["loyalty"],
                "hand": row["hand"],
                "life": row["life"],
                "side": row["side"],
                "subsets": row["subsets"],
                "attractionLights": row["attraction_lights"],
                "faceConvertedManaCost": row["face_converted_mana_cost"],
                "faceManaValue": row["face_mana_value"],
                "faceName": row["face_name"],
                "edhrecRank": row["edhrec_rank"],
                "edhrecSaltiness": row["edhrec_saltiness"],
                "hasAlternativeDeckLimit": row["has_alternative_deck_limit"],
                "identifiers": row["identifiers"],
                "purchaseUrls": row["purchase_urls"],
                "foreignData": row["foreign_data"],
                "legalities": row["legalities"],
                "rulings": row["rulings"],
                "relatedCards": row["related_cards"],
                "leadershipSkills": row["leadership_skills"],
            }

            # Convert embedding from pgvector to list of floats
            if row["embedding_of_text"] is not None:
                # pgvector returns a string like "[0.1,0.2,0.3]"
                embedding_str = row["embedding_of_text"]
                if isinstance(embedding_str, str):
                    # Remove brackets and split by comma
                    embedding_str = embedding_str.strip("[]")
                    card_data["embedding_of_text"] = [
                        float(x) for x in embedding_str.split(",")
                    ]
                else:
                    card_data["embedding_of_text"] = embedding_str
            else:
                card_data["embedding_of_text"] = None

            # Remove None values to keep JSON clean
            card_data = {k: v for k, v in card_data.items() if v is not None}

            # Group by card name (like AtomicCards.json structure)
            card_name = row["name"]
            if card_name not in data_dict:
                data_dict[card_name] = []
            data_dict[card_name].append(card_data)

        # Create final structure
        output_data = {"data": data_dict}

        # Create output directory if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Write to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Successfully exported {len(rows)} cards to {output_file}")
        print(f"📊 Unique card names: {len(data_dict)}")

        # Show file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"📁 File size: {file_size:.2f} MB")

        return True

    except Exception as e:
        print(f"❌ Error during export: {e}")
        raise


if __name__ == "__main__":
    export_cards_to_json()
