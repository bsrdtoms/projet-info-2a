from business_object.card import Card
from service.card_service import CardService

service = CardService()

nouvelle_carte = Card(
    id=None,
    name="Lena",
    text="student data science",
    embedding_of_text=None
)

"""
if service.add_card(nouvelle_carte):
    print("✅ Carte ajouté avec succès !")
else:
    print("❌ Échec de l'ajout.")
"""


if service.delete_card(nouvelle_carte):
    print("✅ Carte supprimée avec succès !")
else:
    print("❌ Échec de la suppression.")

"""

carte = Card(
    id=32555,
    name="Laulau",
    text="student data science",
    embedding_of_text=None
)
if service.modify_card(carte, {"name" : "Lena"}):
    print("✅ Carte modifié avec succès !")
else:
    print("❌ Échec de la modification.")
"""