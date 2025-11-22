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
from service.historical_service import HistoricalService
from utils.log_init import initialize_logs
from technical_components.embedding.ollama_embedding import get_embedding
from utils.auth import (
    create_access_token,
    Token,
    TokenData,
    require_admin,
    require_game_designer,
    require_authenticated
)


# Application initialization
app = FastAPI(title="Magic Cards API")
initialize_logs("MagicSearch API")

# Service initialization
card_service = CardService()
user_service = UserService()
favorite_service = FavoriteService()
historical_service = HistoricalService()


# ==================== PYDANTIC MODELS ====================
class CardModel(BaseModel):
    """Pydantic model for Magic cards"""
    id: Optional[int] = None
    name: str
    text: Optional[str] = None

class UserModel(BaseModel):
    """Pydantic model for users"""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class CompleteUserModel(BaseModel):
    """Pydantic model for users"""
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


# ==================== CARD ROUTES ====================

@app.get("/card/random", response_model=CardModel, tags=["Cards"])
async def random_card():
    """Get a random card"""
    logging.info("Searching for a random card")
    result = card_service.random()
    if not result:
        raise HTTPException(status_code=404, detail="No card found")
    return result


@app.get("/card/name/{name}", response_model=list[CardModel], tags=["Cards"])
async def search_by_name(name: str):
    """Search for cards by name"""
    logging.info(f"Searching for cards by name: {name}")
    result = card_service.search_by_name(name)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No card found for name: {name}"
        )
    return result


@app.get("/card/describe/{id}", tags=["Cards"])
async def describe_by_id(id: int):
    """Get detailed description of a card by ID"""
    logging.info(f"Searching for card by ID: {id}")
    result = card_service.describe_card(id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No card found for ID: {id}"
        )
    return {"id": id, "description": result}


@app.post("/card/semantic_search_with_L2_distance/", tags=["Cards"])
async def semantic_search_l2(query: str, limit: int = 3):
    """Semantic search for cards with L2 distance"""
    logging.info(f"L2 semantic search with: {query} (limit={limit})")
    result = card_service.semantic_search(query, limit)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No matching card found"
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
    """Semantic search for cards with cosine distance"""
    logging.info(f"Cosine semantic search with: {query} (limit={limit})")
    result = card_service.semantic_search(query, limit, "cosine")
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No matching card found"
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


@app.post("/card/{name}/{text}", tags=["game_designer"])
async def create_card(name: str, text: str, current_user: TokenData = Depends(require_game_designer)):
    """Create a new card (requires game_designer role)"""
    logging.info(f"Creating card: {name} by {current_user.email}")
    success = card_service.add_card(name, text)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Error creating card"
        )
    return {"message": f"Card '{name}' created successfully"}


@app.put("/card/{card_id}", tags=["game_designer"])
async def update_card(card_id: int, updates: dict, current_user: TokenData = Depends(require_game_designer)):
    """Update one or more fields of a card (requires game_designer role)"""
    logging.info(f"Updating card ID {card_id} by {current_user.email}")
    card_object = card_service.find_by_id(card_id)
    if not card_object:
        raise HTTPException(
            status_code=404,
            detail=f"Card with ID {card_id} not found"
        )
    success = card_service.modify_card(card_object, updates)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="One or more updates failed"
        )
    return {
        "message": f"Card '{card_object.name}' (ID={card_id}) updated",
        "updates": updates
    }


@app.delete("/card/{card_id}", tags=["game_designer"])
async def delete_card(card_id: int, current_user: TokenData = Depends(require_game_designer)):
    """Delete a card (requires game_designer role)"""
    logging.info(f"Deleting card ID {card_id} by {current_user.email}")
    card_object = card_service.find_by_id(card_id)
    if not card_object:
        raise HTTPException(
            status_code=404,
            detail=f"Card with ID {card_id} not found"
        )
    name = card_object.name
    success = card_service.delete_card(card_object)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Error during deletion"
        )
    return {"message": f"Card '{name}' (ID={card_id}) deleted successfully"}


# ==================== USER ROUTES ====================

@app.post("/user/register", tags=["Users"])
async def register_client(user: UserModel):
    """Public registration - creates client accounts only"""
    logging.info(f"Registering new client: {user.email}")

    # Force type to 'client' for public registration
    success, message, created_user = user_service.create_account(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        user_type="client"  # Always client for public registration
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

@app.post("/user/login", tags=["Users"], response_model=Token)
async def login(email: str, password: str):
    """Log in a user and get a JWT token"""
    logging.info(f"Login attempt for: {email}")
    success, message, session = user_service.login(email, password)
    if not success:
        raise HTTPException(status_code=401, detail=message)

    # Get user information
    user = user_service.find_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Create JWT token
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


@app.get("/user/me", tags=["Users"])
async def get_my_profile(current_user: TokenData = Depends(require_authenticated)):
    """Get your own profile (requires authentication)"""
    logging.info(f"Fetching profile for {current_user.email}")

    user = user_service.find_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_type": user.user_type,
        "is_active": user.is_active
    }



# ==================== ADMIN ROUTES ====================

@app.post("/admin/user/", tags=["Admin"])
async def create_user_as_admin(user: CompleteUserModel, current_user: TokenData = Depends(require_admin)):
    """Create a user account with any role (admin only)"""
    logging.info(f"Creating {user.user_type} account by admin: {current_user.email}")

    # Validate user_type
    valid_types = ["client", "game_designer", "admin"]
    if user.user_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid user type. Must be one of: {', '.join(valid_types)}"
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


@app.put("/admin/user/{user_id}", tags=["Admin"])
async def update_user_as_admin(
    user_id: int,
    user_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    current_user: TokenData = Depends(require_admin)
):
    """Update a user's information (admin only)"""
    logging.info(f"Updating user ID {user_id} by admin: {current_user.email}")

    # Use service layer
    success, message, updates = user_service.update_user(
        user_id=user_id,
        user_type=user_type,
        is_active=is_active,
        first_name=first_name,
        last_name=last_name
    )

    if not success:
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message)
        elif "invalid" in message.lower() or "no updates" in message.lower():
            raise HTTPException(status_code=400, detail=message)
        else:
            raise HTTPException(status_code=500, detail=message)

    return {
        "message": message,
        "user_id": user_id,
        "updates": updates
    }


@app.get("/admin/favorites/{user_id}", tags=["Admin"])
async def get_user_favorites_as_admin(user_id: int, current_user: TokenData = Depends(require_admin)):
    """Get any user's favorites (admin only)"""
    logging.info(f"Admin {current_user.email} fetching favorites for user ID {user_id}")

    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    favorites = favorite_service.list_favorites(user_id)
    return {
        "user_id": user_id,
        "user_email": user.email,
        "favorites": favorites if favorites else []
    }


@app.get("/admin/history/{user_id}", tags=["Admin"])
async def get_user_history_as_admin(
    user_id: int,
    page: int = 1,
    per_page: int = 20,
    current_user: TokenData = Depends(require_admin)
):
    """Get any user's search history (admin only)"""
    logging.info(f"Admin {current_user.email} fetching history for user ID {user_id}")

    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history_data = historical_service.get_paginated_history(user_id, page, per_page)

    return {
        "user_id": user_id,
        "user_email": user.email,
        "searches": history_data["searches"],
        "total": history_data["total"],
        "page": history_data["page"],
        "per_page": history_data["per_page"],
        "total_pages": history_data["total_pages"]
    }


@app.get("/admin/stats", tags=["Admin"])
async def get_global_stats(current_user: TokenData = Depends(require_admin)):
    """Get global platform statistics (admin only)"""
    logging.info(f"Admin {current_user.email} fetching global stats")

    # Get all users
    all_users = user_service.list_all_users()

    # Count by user type
    user_counts = {"client": 0, "game_designer": 0, "admin": 0}
    active_users = 0
    for user in all_users:
        if hasattr(user, 'user_type'):
            user_counts[user.user_type] = user_counts.get(user.user_type, 0) + 1
        if hasattr(user, 'is_active') and user.is_active:
            active_users += 1

    # Get total searches across all users
    total_searches = 0
    for user in all_users:
        total_searches += historical_service.get_history_count(user.id)

    return {
        "users": {
            "total": len(all_users),
            "active": active_users,
            "by_type": user_counts
        },
        "searches": {
            "total": total_searches
        }
    }


@app.get("/user/", tags=["Admin"])
async def list_all_users(current_user: TokenData = Depends(require_admin)):
    """List all users (requires admin role)"""
    logging.info(f"Fetching user list by {current_user.email}")
    return user_service.list_all_users()


@app.get("/user/{user_id}", tags=["Users"])
async def find_user(user_id: int, current_user: TokenData = Depends(require_authenticated)):
    """Get a user by ID (requires authentication)"""
    logging.info(f"Searching for user ID {user_id} by {current_user.email}")

    # Verify that user is requesting their own profile (except admin)
    if current_user.user_id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only view your own profile"
        )

    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_type": user.user_type,
        "is_active": user.is_active
    }


@app.delete("/admin/{user_id}", tags=["Users"])
async def delete_user(user_id: int, current_user: TokenData = Depends(require_admin)):
    """Delete a user (requires admin role)"""
    logging.info(f"Deleting user ID {user_id} by {current_user.email}")
    success, message = user_service.delete_account(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


# ==================== FAVORITE ROUTES ====================

@app.post("/favorites/{card_id}", tags=["Favorites"])
async def add_favorite(card_id: int, current_user: TokenData = Depends(require_authenticated)):
    """Add a card to your favorites (requires authentication)"""
    # Use the user_id from the JWT token
    user_id = current_user.user_id
    logging.info(f"Adding favorite: user_id={user_id}, card_id={card_id} by {current_user.email}")
    success, message = favorite_service.add_favorite(user_id, card_id)
    if not success and "Internal error" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.delete("/favorites/{card_id}", tags=["Favorites"])
async def remove_favorite(card_id: int, current_user: TokenData = Depends(require_authenticated)):
    """Remove a card from your favorites (requires authentication)"""
    # Use the user_id from the JWT token
    user_id = current_user.user_id
    logging.info(f"Removing favorite: user_id={user_id}, card_id={card_id} by {current_user.email}")
    success, message = favorite_service.remove_favorite(user_id, card_id)
    if not success and "Internal error" in message:
        raise HTTPException(status_code=500, detail=message)
    elif not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}


@app.get("/favorites/", response_model=list[CardModel], tags=["Favorites"])
async def list_favorites(current_user: TokenData = Depends(require_authenticated)):
    """List a user's favorite cards (requires authentication)"""

    logging.info(f"Retrieving favorites for user_id={current_user.user_id}")

    favorites = favorite_service.list_favorites(current_user.user_id)

    if not favorites:
        return {"message": "No cards in favorites"}

    return favorites

# ==================== HISTORY ROUTES ====================

# Function helper for optional authentification
async def get_optional_user(authorization: Optional[str] = None) -> Optional[TokenData]:
    """
    Dependance for optional authentification
    Returns TokenData if authentified, None otherwise
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        from utils.auth import decode_token
        return decode_token(token)
    except Exception:
        return None


@app.post("/card/semantic_search_with_L2_distance/", tags=["Cards"])
async def semantic_search_l2(
    query: str, 
    limit: int = 3,
    authorization: Optional[str] = None
):
    """
    Semantic search for cards with L2 distance
    
    **Authentication**: Optional
    - If authenticated (Bearer token in Authorization header), search is saved to history
    - If not authenticated, search works normally but is not saved
    
    **Parameters**:
    - query: Text description of the card you're looking for
    - limit: Number of results to return (default: 3)
    
    **Returns**: List of cards with similarity scores
    """
    # Get user if authenticated (optional)
    current_user = await get_optional_user(authorization)
    user_id = current_user.user_id if current_user else None
    
    logging.info(f"L2 semantic search: '{query}' (limit={limit}, user_id={user_id})")
    
    try:
        # Perform search with optional user_id for history
        result = card_service.semantic_search(query, limit, "L2", user_id=user_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No matching card found"
            )
        
        return {
            "query": query,
            "distance_metric": "L2",
            "results_count": len(result),
            "saved_to_history": user_id is not None,
            "results": [
                {
                    "id": card.id,
                    "name": card.name,
                    "text": card.text,
                    "similarity": similarity,
                }
                for card, similarity in result
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/card/semantic_search_with_cosine_distance/", tags=["Cards"])
async def semantic_search_cosine(
    query: str, 
    limit: int = 3,
    authorization: Optional[str] = None
):
    """
    Semantic search for cards with cosine distance
    
    **Authentication**: Optional
    - If authenticated (Bearer token in Authorization header), search is saved to history
    - If not authenticated, search works normally but is not saved
    
    **Parameters**:
    - query: Text description of the card you're looking for
    - limit: Number of results to return (default: 3)
    
    **Returns**: List of cards with similarity scores
    """
    # Get user if authenticated (optional)
    current_user = await get_optional_user(authorization)
    user_id = current_user.user_id if current_user else None
    
    logging.info(f"Cosine semantic search: '{query}' (limit={limit}, user_id={user_id})")
    
    try:
        # Perform search with optional user_id for history
        result = card_service.semantic_search(query, limit, "cosine", user_id=user_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No matching card found"
            )
        
        return {
            "query": query,
            "distance_metric": "cosine",
            "results_count": len(result),
            "saved_to_history": user_id is not None,
            "results": [
                {
                    "id": card.id,
                    "name": card.name,
                    "text": card.text,
                    "similarity": similarity,
                }
                for card, similarity in result
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


# ==================== HISTORY ENDPOINTS ====================

@app.get("/history", tags=["History"])
async def get_search_history(
    page: int = 1,
    per_page: int = 20,
    current_user: TokenData = Depends(require_authenticated)
):
    """
    Get your search history with pagination
    
    **Authentication**: Required
    
    **Parameters**:
    - page: Page number (starts at 1)
    - per_page: Number of results per page (max 100)
    
    **Returns**: Paginated list of searches with metadata
    """
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    
    if per_page < 1 or per_page > 100:
        raise HTTPException(status_code=400, detail="Per_page must be between 1 and 100")
    
    user_id = current_user.user_id
    logging.info(f"Fetching search history for user_id={user_id} (page={page}, per_page={per_page})")

    try:
        history_data = historical_service.get_paginated_history(user_id, page, per_page)

        # Format the searches for better readability
        formatted_searches = []
        for search in history_data["searches"]:
            formatted_searches.append({
                "id": search.id,
                "query": search.query_text,
                "results_found": search.result_count,
                "date": search.created_at.isoformat(),
                "has_embedding": search.query_embedding is not None
            })

        return {
            "user_id": user_id,
            "searches": formatted_searches,
            "pagination": {
                "total_searches": history_data["total"],
                "current_page": history_data["page"],
                "per_page": history_data["per_page"],
                "total_pages": history_data["total_pages"],
                "has_next": history_data["page"] < history_data["total_pages"],
                "has_previous": history_data["page"] > 1
            }
        }
    except Exception as e:
        logging.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@app.get("/history/stats", tags=["History"])
async def get_search_statistics(current_user: TokenData = Depends(require_authenticated)):
    """
    Get statistics about your search history
    
    **Authentication**: Required
    
    **Returns**: Statistics including total searches, average results, etc.
    """
    user_id = current_user.user_id
    logging.info(f"Fetching search statistics for user_id={user_id}")

    try:
        stats = historical_service.get_stats(user_id)

        if not stats or stats.get('total_searches', 0) == 0:
            return {
                "user_id": user_id,
                "message": "No search history yet",
                "stats": {
                    "total_searches": 0,
                    "total_results": 0,
                    "average_results_per_search": 0,
                    "most_recent_search": None,
                    "oldest_search": None
                }
            }

        return {
            "user_id": user_id,
            "stats": {
                "total_searches": stats['total_searches'],
                "total_results": stats['total_results'],
                "average_results_per_search": round(stats['avg_results'], 2),
                "most_recent_search": stats['most_recent'].isoformat(),
                "oldest_search": stats['oldest'].isoformat()
            }
        }
    except Exception as e:
        logging.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


@app.get("/history/count", tags=["History"])
async def get_search_count(current_user: TokenData = Depends(require_authenticated)):
    """
    Get the total number of searches in your history
    
    **Authentication**: Required
    
    **Returns**: Total count of searches
    """
    user_id = current_user.user_id
    logging.info(f"Counting search history for user_id={user_id}")

    try:
        count = historical_service.get_history_count(user_id)
        return {
            "user_id": user_id, 
            "total_searches": count
        }
    except Exception as e:
        logging.error(f"Error counting history: {e}")
        raise HTTPException(status_code=500, detail=f"Error counting history: {str(e)}")


@app.get("/history/{search_id}", tags=["History"])
async def get_search_by_id(
    search_id: int,
    current_user: TokenData = Depends(require_authenticated)
):
    """
    Get details of a specific search from your history
    
    **Authentication**: Required
    
    **Parameters**:
    - search_id: ID of the search to retrieve
    
    **Returns**: Detailed information about the search
    """
    user_id = current_user.user_id
    logging.info(f"Fetching search {search_id} for user_id={user_id}")

    try:
        # Get user's history to verify ownership
        history = historical_service.get_user_history(user_id, limit=1000)
        
        # Find the specific search
        search = None
        for s in history:
            if s.id == search_id:
                search = s
                break
        
        if not search:
            raise HTTPException(
                status_code=404,
                detail=f"Search {search_id} not found in your history"
            )
        
        return {
            "id": search.id,
            "user_id": search.user_id,
            "query": search.query_text,
            "results_found": search.result_count,
            "date": search.created_at.isoformat(),
            "has_embedding": search.query_embedding is not None,
            "embedding_dimensions": len(search.query_embedding) if search.query_embedding else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching search: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching search: {str(e)}")


@app.post("/history/{search_id}/repeat", tags=["History"])
async def repeat_search(
    search_id: int,
    limit: int = 5,
    current_user: TokenData = Depends(require_authenticated)
):
    """
    Repeat a past search from your history
    
    **Authentication**: Required
    
    **Parameters**:
    - search_id: ID of the search to repeat
    - limit: Number of results to return (default: 5)
    
    **Returns**: New search results (this creates a new history entry)
    """
    user_id = current_user.user_id
    logging.info(f"Repeating search {search_id} for user_id={user_id}")

    try:
        # Get user's history to verify ownership
        history = historical_service.get_user_history(user_id, limit=1000)
        
        # Find the specific search
        search_to_repeat = None
        for s in history:
            if s.id == search_id:
                search_to_repeat = s
                break
        
        if not search_to_repeat:
            raise HTTPException(
                status_code=404,
                detail=f"Search {search_id} not found in your history"
            )
        
        # Perform the search again (will create a new history entry)
        result = card_service.semantic_search(
            search_to_repeat.query_text,
            top_k=limit,
            user_id=user_id
        )
        
        return {
            "original_search_id": search_id,
            "query": search_to_repeat.query_text,
            "new_results_count": len(result),
            "message": "Search repeated and saved as new history entry",
            "results": [
                {
                    "id": card.id,
                    "name": card.name,
                    "text": card.text,
                    "similarity": similarity,
                }
                for card, similarity in result
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error repeating search: {e}")
        raise HTTPException(status_code=500, detail=f"Error repeating search: {str(e)}")


@app.delete("/history/{search_id}", tags=["History"])
async def delete_search(
    search_id: int,
    current_user: TokenData = Depends(require_authenticated)
):
    """
    Delete a specific search from your history
    
    **Authentication**: Required
    
    **Parameters**:
    - search_id: ID of the search to delete
    
    **Returns**: Confirmation message
    """
    user_id = current_user.user_id
    logging.info(f"Deleting search {search_id} for user_id={user_id}")

    try:
        # Get user's history to verify ownership
        history = historical_service.get_user_history(user_id, limit=1000)
        
        # Verify the search belongs to this user
        found = any(s.id == search_id for s in history)
        if not found:
            raise HTTPException(
                status_code=404,
                detail=f"Search {search_id} not found in your history"
            )
        
        # Delete the search
        success = historical_service.delete_search(search_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete search"
            )
        
        return {
            "message": f"Search {search_id} deleted successfully",
            "deleted_search_id": search_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting search: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting search: {str(e)}")


@app.delete("/history", tags=["History"])
async def clear_search_history(current_user: TokenData = Depends(require_authenticated)):
    """
    Clear ALL your search history
    
    **Authentication**: Required
    
    **Warning**: This action cannot be undone!
    
    **Returns**: Confirmation message with count of deleted searches
    """
    user_id = current_user.user_id
    logging.info(f"Clearing ALL search history for user_id={user_id}")

    try:
        # Get count before deletion
        count_before = historical_service.get_history_count(user_id)
        
        # Clear history
        success = historical_service.clear_user_history(user_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to clear history"
            )
        
        return {
            "message": "Search history cleared successfully",
            "deleted_searches": count_before,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


# ==================== ADMIN ENDPOINTS FOR HISTORY ====================

@app.get("/admin/history/{user_id}", tags=["Admin"])
async def get_user_history_as_admin(
    user_id: int,
    page: int = 1,
    per_page: int = 20,
    current_user: TokenData = Depends(require_admin)
):
    """
    Get any user's search history (admin only)
    
    **Authentication**: Admin required
    
    **Parameters**:
    - user_id: ID of the user whose history to retrieve
    - page: Page number (starts at 1)
    - per_page: Number of results per page
    
    **Returns**: Paginated list of user's searches
    """
    logging.info(f"Admin {current_user.email} fetching history for user ID {user_id}")

    try:
        # Verify user exists
        user = user_service.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        history_data = historical_service.get_paginated_history(user_id, page, per_page)

        # Format the searches
        formatted_searches = []
        for search in history_data["searches"]:
            formatted_searches.append({
                "id": search.id,
                "query": search.query_text,
                "results_found": search.result_count,
                "date": search.created_at.isoformat()
            })

        return {
            "user_id": user_id,
            "user_email": user.email,
            "searches": formatted_searches,
            "pagination": {
                "total_searches": history_data["total"],
                "current_page": history_data["page"],
                "per_page": history_data["per_page"],
                "total_pages": history_data["total_pages"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching user history: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user history: {str(e)}")


# ==================== APPLICATION STARTUP ====================

if __name__ == "__main__":
    # Check required environment variables
    required_vars = [
        'API_TOKEN',
        'PGHOST',
        'PGPORT',
        'PGDATABASE',
        'PGUSER',
        'PGPASSWORD',
        'PGSCHEMA',
        'SECRET_KEY',
        'ALGORITHM',
        'ACCESS_TOKEN_EXPIRE_MINUTES'
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        exit(1)

    # Check connection to embeddings API
    try:
        response = get_embedding("test")
        if "embeddings" not in response:
            print("❌ Invalid API_TOKEN")
            exit(1)
    except Exception as e:
        print(f"❌ API Error: {e}")
        exit(1)

    # Start server
    uvicorn.run(app, host="0.0.0.0", port=9876)
    logging.info("Stopping MagicSearch API")
