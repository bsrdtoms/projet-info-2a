from dao.favorite_dao import FavoriteDAO
from utils.log_decorator import log

class FavoriteService:
    def __init__(self):
        self.dao = FavoriteDAO()

    @log
    def add_favorite(self, user_id: int, card_id: int):
        added = self.dao.add_favorite(user_id, card_id)
        if added:
            return True, "Carte ajoutée aux favoris"
        else:
            return False, "La carte est déjà en favoris (ou échec d'ajout)"

    @log
    def remove_favorite(self, user_id: int, card_id: int):
        removed = self.dao.remove_favorite(user_id, card_id)
        if removed :
            return True, "Carte retirée des favoris"
        else :
            return False, "Carte non trouvée"

    @log
    def list_favorites(self, user_id: int):
        return self.dao.list_favorites(user_id)
