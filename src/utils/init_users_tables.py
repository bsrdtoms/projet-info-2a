"""
Script pour initialiser les tables utilisateurs dans la base de données
À exécuter une seule fois après reset_all_the_database.py
"""
import os
from dao.db_connection import DBConnection


def run_sql_file(filepath: str) -> bool:
    """Exécute un fichier SQL"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()

        print(f"✅ Fichier SQL exécuté: {filepath}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du SQL: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("🚀 INITIALISATION DES TABLES UTILISATEURS")
    print("=" * 60 + "\n")

    # Chemin vers le fichier SQL
    sql_file = "data/add_users_tables.sql"

    if not os.path.exists(sql_file):
        print(f"❌ Fichier introuvable: {sql_file}")
        print("   Créez d'abord le fichier SQL avec les tables")
        return

    # Exécuter le fichier SQL
    if run_sql_file(sql_file):
        print("\n" + "=" * 60)
        print("✅ TABLES UTILISATEURS CRÉÉES AVEC SUCCÈS")
        print("=" * 60)
        print("\nCompte admin par défaut:")
        print("  Email: admin@magicsearch.com")
        print("  Mot de passe: admin123")
        print("\n⚠️  N'oubliez pas de changer ce mot de passe en production!")
    else:
        print("\n❌ Échec de l'initialisation")


if __name__ == "__main__":
    main()