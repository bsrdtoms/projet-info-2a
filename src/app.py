import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from service.card_service import CardService
from business_object.card import Card
from utils.log_init import initialiser_logs

app = FastAPI(title="Magic Cards API")

initialiser_logs("MagicSearch API")

card_service = CardService()


# ---------- REDIRECTION ----------
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


# ---------- ROUTES PRINCIPALES ----------
@app.get("/card/random", tags=["Cards"])
async def random_card():
    """Récupérer une carte aléatoire"""
    logging.info("Recherche d'une carte aléatoire")
    result = card_service.random()
    if not result:
        raise HTTPException(status_code=404, detail="Aucune carte trouvée")
    return result


@app.get("/card/name/{name}", tags=["Cards"])
async def search_by_name(name: str):
    """Rechercher une carte par son nom"""
    logging.info(f"Recherche d'une carte par nom : {name}")
    result = card_service.search_by_name(name)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Aucune carte trouvée pour le nom : {name}"
        )
    return result


@app.post("/card/semantic_search/", tags=["Cards"])
async def semantic_search(query: str):
    """Recherche sémantique de carte (par description)"""
    logging.info(f"Recherche sémantique avec : {query}")
    result = card_service.semantic_search(query, 1)
    if not result:
        raise HTTPException(
            status_code=404, detail="Aucune carte correspondante trouvée"
        )
    return result


# ---------- MODELE Pydantic ----------
class CardModel(BaseModel):
    """Modèle Pydantic pour les cartes Magic"""

    id: int | None = None
    name: str
    text: str | None = None


# ---------- CRUD ----------
@app.post("/card/", tags=["Cards"])
async def create_card(card: CardModel):
    """Créer une nouvelle carte"""
    logging.info("Création d'une carte")
    carte_objet = Card(None, card.name, card.text)

    success = card_service.add_card(carte_objet)
    if not success:
        raise HTTPException(
            status_code=500, detail="Erreur lors de la création de la carte"
        )

    return {"message": f"Carte '{card.name}' créée avec succès"}


@app.put("/card/{card_id}", tags=["Cards"])
async def update_card(card_id: int, name: str, updates: dict):
    """Modifier un ou plusieurs champs d'une carte"""
    logging.info(f"Modification de la carte {card_id}")
    carte_objet = card_service.find_by_id(card_id)
    success = card_service.modify_card(carte_objet, updates)
    if not success:
        raise HTTPException(
            status_code=400, detail="Une ou plusieurs modifications ont échoué"
        )
    return {"message": f"Carte {name} (id={card_id}) mise à jour", "updates": updates}


@app.delete("/card/{card_id}", tags=["Cards"])
async def delete_card(card_id: int, name: str):
    """Supprimer une carte"""
    logging.info(f"Suppression de la carte {card_id}")
    carte_objet = Card(card_id, name, None)
    success = card_service.delete_card(carte_objet)
    if not success:
        raise HTTPException(status_code=404, detail="Carte non trouvée")
    return {"message": f"Carte {name} (id={card_id}) supprimée avec succès"}


# ---------- HELLO ----------
@app.get("/hello/{name}", tags=["Test"])
async def hello_name(name: str):
    """Test de l'API"""
    logging.info(f"Hello demandé pour {name}")
    return {"message": f"Hello {name}"}


# ---------- RUN THE FASTAPI APPLICATION ----------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9876)

    logging.info("Arret de MagicSearch API")
