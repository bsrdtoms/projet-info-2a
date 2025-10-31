from business_object.card import Card
from service.card_service import CardService

service = CardService()

nouvelle_carte = Card(
    id=None,
    name="Lightning Bolt",
    text="Lightning Bolt deals 3 damage to any target.",
    embedding_of_text=None
)

"""
if service.add_card(nouvelle_carte):
    print("✅ Carte ajouté avec succès !")
else:
    print("❌ Échec de l'ajout.")
"""

"""
if service.delete_card(nouvelle_carte):
    print("✅ Carte supprimée avec succès !")
else:
    print("❌ Échec de la suppression.")
"""