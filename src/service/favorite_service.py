from dao.favorite_dao import FavoriteDAO
from utils.log_decorator import log

class FavoriteService:
    def __init__(self):
        self.dao = FavoriteDAO()

    @log
    def add_favorite(self, user_id: int, card_id: int):
        added = self.dao.add_favorite(user_id, card_id)
        if added:
            return True, "Card added to favorites"
        else:
            return False, "Card is already in favorites (or failed to add)"

    @log
    def remove_favorite(self, user_id: int, card_id: int):
        removed = self.dao.remove_favorite(user_id, card_id)
        if removed :
            return True, "Card removed from favorites"
        else :
            return False, "Card not found"

    @log
    def list_favorites(self, user_id: int):
        return self.dao.list_favorites(user_id)
