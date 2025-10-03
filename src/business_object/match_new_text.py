import numpy as np
from business_object.use_the_sspcloud_api import get_embedding
from dao.magic_card import MagicCardDao


def cosine_similarity(vec1, vec2):
    """Calcule la similarité cosinus entre deux vecteurs"""
    if vec1 is None or vec2 is None:
        return -1  # Valeur minimale pour les embeddings manquants

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    # Éviter la division par zéro
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0

    return np.dot(vec1, vec2) / (norm1 * norm2)


def match_new_text(text, top_k):
    """
    Trouve les cartes les plus similaires à un texte donné

    Args:
        text (str): Le texte à matcher
        top_k (int): Nombre de cartes similaires à retourner

    Returns:
        pd.DataFrame: DataFrame avec les cartes les plus similaires
    """
    r = get_embedding(text)["embeddings"][0]
    dao = MagicCardDao()
    df_with_embeddings = dao.get_all_embeddings()

    similarities = []

    for idx, row in df_with_embeddings.iterrows():
        embedding = row['embedding_of_text']
        similarity = cosine_similarity(r, embedding)
        similarities.append(similarity)

    df_with_embeddings['similarity'] = similarities

    # 5. Trier par similarité décroissante et prendre le top K
    results = df_with_embeddings.nlargest(top_k, 'similarity')

    return results.iloc[0]["name"]


# Exemple simple
results = match_new_text("Flying creature with deathtouch", top_k=5)

print(type(results))


