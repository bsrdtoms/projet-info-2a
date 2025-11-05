import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from service.card_service import CardService

app = FastAPI(title="Magic Cards API")
logging.basicConfig(level=logging.INFO)

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
        raise HTTPException(status_code=404, detail=f"Aucune carte trouvée pour le nom : {name}")
    return result

@app.post("/card/semantic_search/", tags=["Cards"])
async def semantic_search(query: str):
    """Recherche sémantique de carte (par description)"""
    logging.info(f"Recherche sémantique avec : {query}")
    result = card_service.semantic_search(query,1)
    if not result:
        raise HTTPException(status_code=404, detail="Aucune carte correspondante trouvée")
    return result



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

    logging.info("Arret du Webservice")
