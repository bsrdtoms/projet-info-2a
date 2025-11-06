import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional

from service.card_service import CardService
from business_object.card import Card # attention, l'API doit communiquer avec le service uniquement

from service.user_service import UserService

from utils.log_init import initialiser_logs

app = FastAPI(title="Magic Cards API")

initialiser_logs("MagicSearch API")


# ---------- REDIRECTION ----------
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")

# 1. ---------- CARTES ----------

card_service = CardService()

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

# 1. ---------- USER ----------
user_service = UserService()

# ---------- MODELE Pydantic ----------
class UserModel(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str = "client"
    is_active: bool = True

# ---------- ROUTES PRINCIPALES ----------
@app.post("/user/", tags=["Users"])
async def create_user(user: UserModel):
    """Créer un nouveau compte utilisateur"""
    logging.info(f"Tentative de création du compte {user.email}")
    success, message, created_user = user_service.create_account(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        user_type=user.user_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "user": created_user.email}

@app.post("/user/login", tags=["Users"])
async def login(email: str, password: str):
    """Connecter un utilisateur"""
    logging.info(f"Tentative de connexion pour {email}")
    success, message, session = user_service.login(email, password)
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return {"message": message, "session_id": session.session_id}

@app.post("/user/logout", tags=["Users"])
async def logout():
    """Déconnecter l’utilisateur courant"""
    success, message = user_service.logout()
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.get("/user/", tags=["Users"])
async def list_all_users():
    """Lister tous les utilisateurs (admin uniquement)"""
    logging.info("Récupération de la liste des utilisateurs")
    return user_service.list_all_users()

@app.get("/user/{user_id}", tags=["Users"])
async def find_user(user_id: int):
    """Trouver un utilisateur par ID"""
    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_type": user.user_type,
        "is_active": user.is_active
    }

@app.delete("/user/{user_id}", tags=["Users"])
async def delete_user(user_id: int):
    """Supprimer un utilisateur"""
    logging.info(f"Suppression de l'utilisateur {user_id}")
    success, message = user_service.delete_account(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


# ---------- CRUD ----------




# ---------- RUN THE FASTAPI APPLICATION ----------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9876)

    logging.info("Arret de MagicSearch API")
