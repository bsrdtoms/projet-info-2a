from pydantic import BaseModel
from typing import List, Dict, Optional


class Identifiers(BaseModel):
    """Identifiants uniques de la carte"""
    scryfallOracleId: Optional[str] = None


class PurchaseUrls(BaseModel):
    """Liens pour acheter la carte"""
    cardKingdom: Optional[str] = None
    cardKingdomFoil: Optional[str] = None
    cardmarket: Optional[str] = None
    tcgplayer: Optional[str] = None


class CardModel(BaseModel):
    """Modèle Pydantic pour une carte MTG"""

    name: str
    type: str
    layout: str
    text: Optional[str] = None

    colors: Optional[List[str]] = []
    colorIdentity: Optional[List[str]] = []

    manaCost: Optional[str] = None
    manaValue: Optional[float] = None
    convertedManaCost: Optional[float] = None

    firstPrinting: Optional[str] = None
    printings: Optional[List[str]] = []

    isFunny: Optional[bool] = None

    subtypes: Optional[List[str]] = []
    supertypes: Optional[List[str]] = []
    types: Optional[List[str]] = []

    foreignData: Optional[List[dict]] = []   # si tu veux, tu peux faire un modèle dédié

    identifiers: Optional[Identifiers] = None
    purchaseUrls: Optional[PurchaseUrls] = None

    legalities: Optional[Dict[str, str]] = {}
    rulings: Optional[List[dict]] = []

    # Champs numériques optionnels (souvent null dans les JSON)
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None

    # Exemple d’un champ très spécifique
    embedding_of_text: Optional[List[float]] = None
