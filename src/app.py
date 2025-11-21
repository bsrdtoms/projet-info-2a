import logging
import os

from fastapi import FastAPI, HTTPException, Depends
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
from utils.auth import (
    create_access_token,
    Token,
    TokenData,
    get_current_user,
    require_admin,
    require_game_designer,
    require_authenticated
)

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
    id: Optional[int] = None
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str = "client"
    is_active: bool = True


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
async def create_card(name: str, text: str, current_user: TokenData = Depends(require_game_designer)):
    """Créer une nouvelle carte (nécessite le rôle game_designer)"""
    logging.info(f"Création d'une carte : {name} par {current_user.email}")
    carte_objet = Card(None, name, text)
    success = card_service.add_card(carte_objet)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la création de la carte"
        )
    return {"message": f"Carte '{carte_objet.name}' créée avec succès"}


@app.put("/card/{card_id}", tags=["Cards"])
async def update_card(card_id: int, updates: dict, current_user: TokenData = Depends(require_game_designer)):
    """Modifier un ou plusieurs champs d'une carte (nécessite le rôle game_designer)"""
    logging.info(f"Modification de la carte ID {card_id} par {current_user.email}")
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
async def delete_card(card_id: int, current_user: TokenData = Depends(require_game_designer)):
    """Supprimer une carte (nécessite le rôle game_designer)"""
    logging.info(f"Suppression de la carte ID {card_id} par {current_user.email}")
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

@app.post("/user/register", tags=["Users"])
async def register_client(user: UserModel):
    """Inscription publique - crée uniquement des comptes client"""
    logging.info(f"Inscription d'un nouveau client : {user.email}")

    # Forcer le type à 'client' pour l'inscription publique
    success, message, created_user = user_service.create_account(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        user_type="client"  # Toujours client pour l'inscription publique
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {
        "message": message,
        "user": {
            "email": created_user.email,
            "user_type": created_user.user_type
        }
    }


@app.post("/admin/user/", tags=["Admin"])
async def create_user_as_admin(user: UserModel, current_user: TokenData = Depends(require_admin)):
    """Créer un compte utilisateur avec n'importe quel rôle (admin uniquement)"""
    logging.info(f"Création d'un compte {user.user_type} par admin : {current_user.email}")

    # Valider le user_type
    valid_types = ["client", "game_designer", "admin"]
    if user.user_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Type d'utilisateur invalide. Doit être l'un de: {', '.join(valid_types)}"
        )

    success, message, created_user = user_service.create_account(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        user_type=user.user_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {
        "message": message,
        "user": {
            "email": created_user.email,
            "user_type": created_user.user_type,
            "id": created_user.id
        }
    }


@app.post("/user/login", tags=["Users"], response_model=Token)
async def login(email: str, password: str):
    """Connecter un utilisateur et obtenir un token JWT"""
    logging.info(f"Tentative de connexion pour : {email}")
    success, message, session = user_service.login(email, password)
    if not success:
        raise HTTPException(status_code=401, detail=message)

    # Récupérer les informations de l'utilisateur
    user = user_service.find_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Créer le token JWT
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        user_type=user.user_type
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        user_type=user.user_type
    )


@app.post("/user/logout", tags=["Users"])
async def logout():
    """Déconnecter l'utilisateur courant"""
    logging.info("Tentative de déconnexion")
    success, message = user_service.logout()
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.get("/user/me", tags=["Users"])
async def get_my_profile(current_user: TokenData = Depends(require_authenticated)):
    """Récupérer son propre profil (nécessite authentification)"""
    logging.info(f"Récupération du profil pour {current_user.email}")

    user = user_service.find_by_id(current_user.user_id)
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


@app.get("/user/", tags=["Users"])
async def list_all_users(current_user: TokenData = Depends(require_admin)):
    """Lister tous les utilisateurs (nécessite le rôle admin)"""
    logging.info(f"Récupération de la liste des utilisateurs par {current_user.email}")
    return user_service.list_all_users()


@app.get("/user/{user_id}", tags=["Users"])
async def find_user(user_id: int, current_user: TokenData = Depends(require_authenticated)):
    """Récupérer un utilisateur par ID (nécessite authentification)"""
    logging.info(f"Recherche de l'utilisateur ID {user_id} par {current_user.email}")

    # Vérifier que l'utilisateur demande son propre profil (sauf admin)
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez consulter que votre propre profil"
        )

    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur avec l'ID {user_id} introuvable"
        )
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_type": user.user_type,
        "is_active": user.is_active
    }


@app.delete("/user/{user_id}", tags=["Users"])
async def delete_user(user_id: int, current_user: TokenData = Depends(require_admin)):
    """Supprimer un utilisateur (nécessite le rôle admin)"""
    logging.info(f"Suppression de l'utilisateur ID {user_id} par {current_user.email}")
    success, message = user_service.delete_account(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


# ==================== ROUTES FAVORIS ====================

@app.post("/favorites/{card_id}/{user_id}", tags=["Favorites"])
async def add_favorite(card_id: int, user_id: int, current_user: TokenData = Depends(require_authenticated)):
    """Ajouter une carte aux favoris d'un utilisateur (nécessite authentification)"""
    # Vérifier que l'utilisateur ne peut modifier que ses propres favoris (sauf admin)
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez gérer que vos propres favoris"
        )
    logging.info(f"Ajout d'un favori : user_id={user_id}, card_id={card_id} par {current_user.email}")
    success, message = favorite_service.add_favorite(user_id, card_id)
    if not success and "Erreur interne" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.delete("/favorites/{card_id}/{user_id}", tags=["Favorites"])
async def remove_favorite(card_id: int, user_id: int, current_user: TokenData = Depends(require_authenticated)):
    """Supprimer une carte des favoris d'un utilisateur (nécessite authentification)"""
    # Vérifier que l'utilisateur ne peut modifier que ses propres favoris (sauf admin)
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez gérer que vos propres favoris"
        )
    logging.info(f"Suppression d'un favori : user_id={user_id}, card_id={card_id} par {current_user.email}")
    success, message = favorite_service.remove_favorite(user_id, card_id)
    if not success and "Erreur interne" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}


@app.get("/favorites/{user_id}", tags=["Favorites"])
async def list_favorites(user_id: int, response_model=list[CardModel], current_user: TokenData = Depends(require_authenticated)):
    """Lister les cartes favorites d'un utilisateur (nécessite authentification)"""
    # Vérifier que l'utilisateur ne peut voir que ses propres favoris (sauf admin)
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez voir que vos propres favoris"
        )
    logging.info(f"Récupération des favoris pour user_id={user_id} par {current_user.email}")
    favorites = favorite_service.list_favorites(user_id)
    if not favorites:
        return {"message": "Aucune carte en favori"}
    return favorites

# ==================== ROUTES HISTORIQUE ====================

@app.get("/history/{user_id}", tags=["History"])
async def get_search_history(
    user_id: int,
    limit: int = 50,
    current_user: TokenData = Depends(require_authenticated)
):
    """
    Récupère l'historique de recherche d'un utilisateur
    (nécessite authentification)
    """
    # Vérifier que l'utilisateur ne peut voir que son historique
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez voir que votre propre historique"
        )

    history_service = HistoricalSearchService()
    history = history_service.get_history(user_id, limit)

    if not history:
        return {"message": "Aucune recherche dans l'historique"}

    return [
        {
            "id": search.id,
            "query": search.query_text,
            "result_count": search.result_count,
            "created_at": search.created_at.isoformat()
        }
        for search in history
    ]


@app.delete("/history/{search_id}", tags=["History"])
async def delete_search_history(
    search_id: int,
    current_user: TokenData = Depends(require_authenticated)
):
    """Supprime une entrée d'historique spécifique"""
    history_service = HistoricalSearchService()
    success = history_service.delete_search(search_id)

    if not success:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")

    return {"message": "Entrée d'historique supprimée"}


@app.delete("/history/user/{user_id}", tags=["History"])
async def clear_all_history(
    user_id: int,
    current_user: TokenData = Depends(require_authenticated)
):
    """Supprime tout l'historique d'un utilisateur"""
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")

    history_service = HistoricalSearchService()
    history_service.clear_history(user_id)

    return {"message": "Historique complètement supprimé"}


@app.get("/history/stats/{user_id}", tags=["History"])
async def get_search_stats(
    user_id: int,
    current_user: TokenData = Depends(require_authenticated)
):
    """Récupère les statistiques de recherche d'un utilisateur"""
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")

    history_service = HistoricalSearchService()
    stats = history_service.get_stats(user_id)

    if not stats:
        return {"message": "Aucune statistique disponible"}

    return stats

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