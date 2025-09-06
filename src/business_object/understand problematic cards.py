import json
import pandas as pd
import os
import requests
from datetime import datetime
import time


def get_batch_embeddings(texts, batch_size=1000):
    """Obtenir des embeddings en batch"""
    token = os.getenv("API_TOKEN")
    url = "https://llm.lab.sspcloud.fr/ollama/api/embed"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "bge-m3:latest", 
        "input": texts  # Array de textes
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if 'embeddings' in result:
            return result['embeddings']
        elif 'embedding' in result:
            # Si un seul embedding retourné, le répéter
            return [result['embedding']] * len(texts)
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


def process_cards_with_batch():
    """Traitement optimisé des cartes avec batch processing"""
    
    print("📥 Chargement des données...")
    with open("projet-info-2a/data/AtomicCards.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Certaines cartes ont plusieurs versions → on les met toutes dans une liste
    cards = []
    for name, versions in data["data"].items():
        for card in versions:
            cards.append(card)

    df = pd.DataFrame(cards)
    print(f"📊 Total de cartes: {len(df)}")
    
    # Préparer les textes et les indices
    texts_to_embed = []
    valid_indices = []
    
    for i, row in df.iterrows():
        if 'text' in row and row['text'] is not None and str(row['text']).strip():
            texts_to_embed.append(str(row['text']))
            valid_indices.append(i)
        else:
            # Essayer le flavorText si pas de text
            flavor = None
            if 'flavorText' in row and row['flavorText']:
                flavor = row['flavorText']
            elif 'foreignData' in row and row['foreignData']:
                # Prendre le flavor text anglais ou le premier disponible
                for foreign in row['foreignData']:
                    if 'flavorText' in foreign and foreign['flavorText']:
                        flavor = foreign['flavorText']
                        break

            if flavor and str(flavor).strip():
                texts_to_embed.append(str(flavor))
                valid_indices.append(i)

    print(f"📝 Textes à traiter: {len(texts_to_embed)}")
    print(f"📝 Cartes sans texte: {len(df) - len(texts_to_embed)}")

    # Initialiser la colonne embedding
    df["embedding_of_text"] = None

    if len(texts_to_embed) == 0:
        print("⚠️ Aucun texte à traiter!")
        return df

    # Traitement par batch
    batch_size = 1000  # Ajustez selon les limites de l'API
    start_time = time.time()

    try:
        print(f"🚀 Traitement par batch de {batch_size}...")

        for batch_start in range(0, len(texts_to_embed), batch_size):
            batch_end = min(batch_start + batch_size, len(texts_to_embed))
            batch_texts = texts_to_embed[batch_start:batch_end]
            batch_indices = valid_indices[batch_start:batch_end]

            print(f"📦 Batch {batch_start//batch_size + 1}: textes {batch_start+1}-{batch_end}")

            try:
                # Appel batch
                embeddings = get_batch_embeddings(batch_texts, batch_size)

                # Assigner les embeddings
                for i, embedding in enumerate(embeddings):
                    df_index = batch_indices[i]
                    df.at[df_index, "embedding_of_text"] = embedding

                print(f"✅ Batch traité: {len(embeddings)} embeddings")

                # Sauvegarde intermédiaire
                if batch_end % 5000 == 0 or batch_end == len(texts_to_embed):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = f"projet-info-2a/data/cards_progress_{batch_end}_{timestamp}.pkl"
                    df.to_pickle(backup_file)
                    print(f"💾 Sauvegarde: {backup_file}")

            except Exception as e:
                print(f"❌ Erreur batch {batch_start//batch_size + 1}: {e}")
                print("🔄 Fallback vers traitement individuel pour ce batch...")

                # Fallback individuel pour ce batch
                from use_the_sspcloud_api import get_embedding
                for i, text in enumerate(batch_texts):
                    try:
                        df_index = batch_indices[i]
                        embedding = get_embedding(text)
                        if isinstance(embedding, dict) and 'embedding' in embedding:
                            df.at[df_index, "embedding_of_text"] = embedding['embedding']
                        else:
                            df.at[df_index, "embedding_of_text"] = embedding
                    except Exception as e2:
                        print(f"❌ Erreur carte individuelle: {e2}")
                        continue

        elapsed = time.time() - start_time
        print(f"⏱️ Temps total: {elapsed/60:.1f} minutes")

    except Exception as e:
        print(f"❌ Erreur majeure: {e}")
        print("🔄 Fallback complet vers traitement individuel...")

        # Fallback complet
        from use_the_sspcloud_api import get_embedding
        for i, text in enumerate(texts_to_embed):
            try:
                df_index = valid_indices[i]
                embedding = get_embedding(text)
                df.at[df_index, "embedding_of_text"] = embedding
                if (i + 1) % 100 == 0:
                    print(f"✅ {i+1}/{len(texts_to_embed)} traités individuellement")

            except:
                continue

    # Sauvegarde finale
    print("💾 Sauvegardes finales...")

    # Pickle (le plus sûr)
    df.to_pickle("projet-info-2a/data/cards_with_embeddings_final.pkl")
    print("✅ Pickle sauvegardé")

    # JSON
    try:
        df.to_json("projet-info-2a/data/cards_with_embeddings.json",
                   orient="records", lines=True, force_ascii=False)
        print("✅ JSON sauvegardé")
    except Exception as e:
        print(f"⚠️ Erreur JSON: {e}")

    # Statistiques
    successful = df['embedding_of_text'].notna().sum()
    print(f"📈 Résultat final: {successful}/{len(df)} embeddings calculés")

    return df


# Lancement
if __name__ == "__main__":
    df_result = process_cards_with_batch()
