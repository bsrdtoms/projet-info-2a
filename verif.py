import os
import dotenv

dotenv.load_dotenv()
print(os.environ["POSTGRES_USER"])

# 🔧 Remplace par la valeur que tu attends
valeur_attendue = "user-id2638"

# ✅ Récupération de la variable d'environnement
valeur_actuelle = os.getenv("POSTGRE_USER")

# 🧠 Vérification
if valeur_actuelle is None:
    print("❌ La variable d'environnement POSTGRE_USER n'est pas définie.")
elif valeur_actuelle == valeur_attendue:
    print(f"✅ POSTGRE_USER est bien définie avec la bonne valeur : {valeur_actuelle}")
else:
    print(f"⚠️ POSTGRE_USER est définie avec une autre valeur : {valeur_actuelle}")
    print(f"👉 Valeur attendue : {valeur_attendue}")
