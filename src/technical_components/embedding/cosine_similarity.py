import numpy as np

def cosine_similarity(vec1, vec2):
    """Calcule la similarité cosinus entre deux vecteurs"""
    if vec1 is None or vec2 is None:
        return -1  # Valeur minimale pour embeddings manquants

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)
