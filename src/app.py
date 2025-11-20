import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn

from service.card_service import CardService
from service.user_service import UserService
from service.favorite_service import FavoriteService
from business_object.card import Card
from utils.log_init import initialiser_logs
from technical_components.embedding.ollama_embedding import get_embedding


# Initialisation de l'application
app = FastAPI(title="Magic Cards API")
initialiser_logs("MagicSearch API")

# Initialisation des services
card_service = CardService()
user_service = UserService()
favorite_service = FavoriteService()


# ==================== MODÈLES PYDANTIC ====================
class CardModel(BaseModel):
    """Modèle Pydantic pour les cartes Magic"""
    id: Optional[int] = None
    name: str
    text: Optional[str] = None


class UserModel(BaseModel):
    """Modèle Pydantic pour les utilisateurs"""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# ==================== REDIRECTION ====================

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


# ==================== ROUTES CARTES ====================

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
    """Rechercher des cartes par nom"""
    logging.info(f"Recherche de cartes par nom : {name}")
    result = card_service.search_by_name(name)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Aucune carte trouvée pour le nom : {name}"
        )
    return result


@app.get("/card/describe/{id}", tags=["Cards"])
async def describe_by_id(id: int):
    """Récupérer la description détaillée d'une carte par ID"""
    logging.info(f"Recherche d'une carte par ID : {id}")
    result = card_service.describe_card(id)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Aucune carte trouvée pour l'ID : {id}"
        )
    return result


@app.post("/card/semantic_search_with_L2_distance/", tags=["Cards"])
async def semantic_search_l2(query: str, limit: int = 3):
    """Recherche sémantique de cartes avec distance L2"""
    logging.info(f"Recherche sémantique L2 avec : {query} (limit={limit})")
    result = card_service.semantic_search(query, limit)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Aucune carte correspondante trouvée"
        )
    return [
        {
            "id": card.id,
            "name": card.name,
            "text": card.text,
            "similarity": similarity,
        }
        for card, similarity in result
    ]


@app.post("/card/semantic_search_with_cosine_distance/", tags=["Cards"])
async def semantic_search_cosine(query: str, limit: int = 3):
    """Recherche sémantique de cartes avec distance cosinus"""
    logging.info(f"Recherche sémantique cosinus avec : {query} (limit={limit})")
    result = card_service.semantic_search(query, limit, "cosine")
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Aucune carte correspondante trouvée"
        )
    return [
        {
            "id": card.id,
            "name": card.name,
            "text": card.text,
            "similarity": similarity,
        }
        for card, similarity in result
    ]


@app.post("/card/{name}/{text}", tags=["Cards"])
async def create_card(name: str, text: str):
    """Créer une nouvelle carte"""
    logging.info(f"Création d'une carte : {name}")
    carte_objet = Card(None, name, text)
    success = card_service.add_card(carte_objet)
    if not success:
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la création de la carte"
        )
    return {"message": f"Carte '{carte_objet.name}' créée avec succès"}


@app.put("/card/{card_id}", tags=["Cards"])
async def update_card(card_id: int, updates: dict):
    """Modifier un ou plusieurs champs d'une carte"""
    logging.info(f"Modification de la carte ID {card_id}")
    carte_objet = card_service.find_by_id(card_id)
    if not carte_objet:
        raise HTTPException(
            status_code=404, 
            detail=f"Carte avec l'ID {card_id} introuvable"
        )
    success = card_service.modify_card(carte_objet, updates)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Une ou plusieurs modifications ont échoué"
        )
    return {
        "message": f"Carte '{carte_objet.name}' (ID={card_id}) mise à jour",
        "updates": updates
    }


@app.delete("/card/{card_id}", tags=["Cards"])
async def delete_card(card_id: int):
    """Supprimer une carte"""
    logging.info(f"Suppression de la carte ID {card_id}")
    carte_objet = card_service.find_by_id(card_id)
    if not carte_objet:
        raise HTTPException(
            status_code=404, 
            detail=f"Carte avec l'ID {card_id} introuvable"
        )
    name = carte_objet.name
    success = card_service.delete_card(carte_objet)
    if not success:
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la suppression"
        )
    return {"message": f"Carte '{name}' (ID={card_id}) supprimée avec succès"}


# ==================== ROUTES UTILISATEURS ====================

@app.post("/user/", tags=["Users"])
async def create_user(user: UserModel):
    """Créer un nouveau compte utilisateur"""
    logging.info(f"Tentative de création du compte : {user.email}")
    success, message, created_user = user_service.create_account(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "user": created_user.email, "id": created_user.id}


@app.post("/user/login", tags=["Users"])
async def login(email: str, password: str):
    """Connecter un utilisateur"""
    logging.info(f"Tentative de connexion pour : {email}")
    success, message, session = user_service.login(email, password)
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return {"message": message, "session_id": session.session_id}


@app.post("/user/logout", tags=["Users"])
async def logout():
    """Déconnecter l'utilisateur courant"""
    logging.info("Tentative de déconnexion")
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
    """Récupérer un utilisateur par ID"""
    logging.info(f"Recherche de l'utilisateur ID {user_id}")
    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=f"Utilisateur avec l'ID {user_id} introuvable"
        )
    return user_service.find_by_id(user_id)


@app.delete("/user/{user_id}", tags=["Users"])
async def delete_user(user_id: int):
    """Supprimer un utilisateur"""
    logging.info(f"Suppression de l'utilisateur ID {user_id}")
    success, message = user_service.delete_account(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


# ==================== ROUTES FAVORIS ====================

@app.post("/favorites/{card_id}/{user_id}", tags=["Favorites"])
async def add_favorite(card_id: int, user_id: int):
    """Ajouter une carte aux favoris d'un utilisateur"""
    logging.info(f"Ajout d'un favori : user_id={user_id}, card_id={card_id}")
    success, message = favorite_service.add_favorite(user_id, card_id)
    if not success and "Erreur interne" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.delete("/favorites/{card_id}/{user_id}", tags=["Favorites"])
async def remove_favorite(card_id: int, user_id: int):
    """Supprimer une carte des favoris d'un utilisateur"""
    logging.info(f"Suppression d'un favori : user_id={user_id}, card_id={card_id}")
    success, message = favorite_service.remove_favorite(user_id, card_id)
    if not success and "Erreur interne" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}


@app.get("/favorites/{user_id}", tags=["Favorites"])
async def list_favorites(user_id: int):
    """Lister les cartes favorites d'un utilisateur"""
    logging.info(f"Récupération des favoris pour user_id={user_id}")
    favorites = favorite_service.list_favorites(user_id)
    if not favorites:
        return {"message": "Aucune carte en favori"}
    return favorites


# ==================== DÉMARRAGE DE L'APPLICATION ====================

if __name__ == "__main__":
    # Vérification des variables d'environnement requises
    required_vars = [
        'API_TOKEN', 
        'POSTGRES_HOST', 
        'POSTGRES_PORT', 
        'POSTGRES_DATABASE',
        'POSTGRES_USER', 
        'POSTGRES_PASSWORD', 
        'POSTGRES_SCHEMA'
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Variables d'environnement manquantes : {', '.join(missing)}")
        exit(1)

    # Vérification de la connexion à l'API d'embeddings
    try:
        response = get_embedding("test")
        if "embeddings" not in response:
            print("❌ API_TOKEN invalide")
            exit(1)
    except Exception as e:
        print(f"❌ Erreur API : {e}")
        exit(1)

    # Démarrage du serveur
    uvicorn.run(app, host="0.0.0.0", port=9876)
    logging.info("Arrêt de MagicSearch API")