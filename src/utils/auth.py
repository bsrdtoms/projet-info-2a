"""
JWT Authentication and Authorization utilities for the Magic Cards API
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
import dotenv

dotenv.load_dotenv()  # loads variables from .env

# Configuration
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])


# Security scheme
security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data"""

    user_id: int
    email: str
    user_type: str
    exp: Optional[datetime] = None


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    user_type: str


def create_access_token(
    user_id: int, email: str, user_type: str, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token

    Args:
        user_id: User's ID
        email: User's email
        user_type: User's role (client, game_designer, admin)
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "user_id": user_id,
        "email": email,
        "user_type": user_type,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        TokenData object with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        user_type: str = payload.get("user_type")

        if user_id is None or email is None or user_type is None:
            raise credentials_exception

        return TokenData(user_id=user_id, email=email, user_type=user_type)

    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Dependency to get the current authenticated user from the JWT token

    Args:
        credentials: HTTP Authorization credentials with Bearer token

    Returns:
        TokenData object with current user information

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    return decode_token(token)


async def require_admin(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    Dependency to require admin role

    Args:
        current_user: Current authenticated user

    Returns:
        TokenData if user is admin

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


async def require_game_designer(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    Dependency to require game_designer role (or admin)

    Args:
        current_user: Current authenticated user

    Returns:
        TokenData if user is game_designer or admin

    Raises:
        HTTPException: If user is not a game_designer or admin
    """
    if current_user.user_type not in ["game_designer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Game Designer privileges required",
        )
    return current_user


async def require_authenticated(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    Dependency to require any authenticated user

    Args:
        current_user: Current authenticated user

    Returns:
        TokenData for any authenticated user
    """
    return current_user
