import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional

from service.card_service import CardService
from business_object.card import Card # attention, l'API doit communiquer avec le service uniquement

from service.user_service import UserService

from service.favorite_service import FavoriteService

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


# ---------- MODELE Pydantic ----------
class CardModel(BaseModel):
    """Modèle Pydantic pour les cartes Magic"""

    id: int | None = None
    name: str
    text: str | None = None

# ---------- ROUTES PRINCIPALES ----------
@app.get("/card/random", response_model=CardModel, tags=["Cards"])
async def random_card():
    """Récupérer une carte aléatoire"""
    logging.info("Recherche d'une carte aléatoire")
    result = card_service.random()
    if not result:
        raise HTTPException(status_code=404, detail="Aucune carte trouvée")
    return result


@app.get("/card/name/{name}", response_model=list[CardModel], tags=["Cards"])
async def search_by_name(name: str):
    """Rechercher une carte par son nom"""
    logging.info(f"Recherche d'une carte par nom : {name}")
    result = card_service.search_by_name(name)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Aucune carte trouvée pour le nom : {name}"
        )
    return result


@app.get("/card/describe/{id}", tags=["Cards"])
async def describe_by_id(id: int):
    """Rechercher une carte par son id"""
    logging.info(f"Recherche d'une carte par nom : {id}")
    result = card_service.describe_card(id)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Aucune carte trouvée pour l'id' : {id}"
        )
    return result


@app.post("/card/semantic_search_with_L2_distance/", tags=["Cards"])
async def semantic_search(query: str):
    """Recherche sémantique de carte (par description)"""
    logging.info(f"Recherche sémantique avec : {query}")
    result = card_service.semantic_search(query, 3)
    if not result:
        raise HTTPException(
            status_code=404, detail="Aucune carte correspondante trouvée"
        )
    return result


@app.post("/card/semantic_search_with_cosine_distance/", tags=["Cards"])
async def semantic_search_cos(query: str):
    """Recherche sémantique de carte (par description)"""
    logging.info(f"Recherche sémantique avec : {query}")

    result = card_service.semantic_search(query, 3, "cosine")
    if not result:
        raise HTTPException(
            status_code=404, detail="Aucune carte correspondante trouvée"
        )
    return result


# ---------- CRUD ----------
@app.post("/card/{name}/{text}", tags=["Cards"])
async def create_card(name: str, text: str):
    """Créer une nouvelle carte"""
    logging.info("Création d'une carte")
    carte_objet = Card(None, name, text)
    success = card_service.add_card(carte_objet)
    if not success:
        raise HTTPException(
            status_code=500, detail="Erreur lors de la création de la carte"
        )

    return {"message": f"Carte '{carte_objet.name}' créée avec succès"}


@app.put("/card/{card_id}", tags=["Cards"])
async def update_card(card_id: int, updates: dict):
    """Modifier un ou plusieurs champs d'une carte"""
    logging.info(f"Modification de la carte {card_id}")
    carte_objet = card_service.find_by_id(card_id)
    success = card_service.modify_card(carte_objet, updates)
    if not success:
        raise HTTPException(
            status_code=400, detail="Une ou plusieurs modifications ont échoué"
        )
    return {"message": f"Carte {carte_objet.name} (id={card_id}) mise à jour", "updates": updates}

@app.delete("/card/{card_id}", tags=["Cards"])
async def delete_card(card_id: int):
    """Supprimer une carte"""
    logging.info(f"Suppression de la carte {card_id}")
    carte_objet = card_service.find_by_id(card_id)
    name = carte_objet.name
    success = card_service.delete_card(carte_objet)
    if not success:
        raise HTTPException(status_code=404, detail="Carte non trouvée")
    return {"message": f"Carte {name} (id={card_id}) supprimée avec succès"}


# 2. ---------- USER ----------
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


# 3. ---------- FAVORIS ----------
favorite_service = FavoriteService()

@app.post("/favorites/{card_id}/{user_id}", tags=["Favorites"])
async def add_favorite(card_id: int, user_id: int):
    """Ajouter une carte aux favoris"""
    logging.info(f"Ajout d’un favori : user={user_id}, card={card_id}")
    success, message = favorite_service.add_favorite(user_id, card_id)
    if not success and "Erreur interne" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.delete("/favorites/{card_id}/{user_id}", tags=["Favorites"])
async def remove_favorite(card_id: int, user_id: int):
    """Supprimer une carte des favoris"""
    logging.info(f"Suppression d’un favori : user={user_id}, card={card_id}")
    success, message = favorite_service.remove_favorite(user_id, card_id)
    if not success and "Erreur interne" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}


@app.get("/favorites/{user_id}", tags=["Favorites"])
async def list_favorites(user_id: int):
    """Lister les cartes favorites d’un utilisateur"""
    logging.info(f"Liste des favoris pour user={user_id}")
    favorites = favorite_service.list_favorites(user_id)
    if not favorites:
        return {"message": "Aucune carte en favori"}
    return favorites


# ---------- RUN THE FASTAPI APPLICATION ----------
if __name__ == "__main__":
    import uvicorn
    import os
    from technical_components.embedding.ollama_embedding import get_embedding

    # A few tests to verify that the user set up well it's environement variable
    required_vars = ['API_TOKEN', 'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DATABASE',
                     'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_SCHEMA']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        exit(1)

    try:
        response = get_embedding("test")

        if "embeddings" not in response:
            print("❌ Invalid API_TOKEN")
            exit(1)

    except Exception as e:
        print(f"❌ API Error: {e}")
        exit(1)

    uvicorn.run(app, host="0.0.0.0", port=9876)

    logging.info("Arret de MagicSearch API")
