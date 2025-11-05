"""
Script de configuration de pgvector pour la base de données
À exécuter une seule fois après la création de la base de données

Usage:
    python src/setup_pgvector.py
"""

import os
import dotenv
from dao.db_connection import DBConnection


class PgVectorSetup:
    """Configure pgvector dans la base de données"""

    def run_query(self, sql: str, fetch_result: bool = False):
        """Exécuter une requête SQL"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    if fetch_result:
                        result = cursor.fetchone()
                        connection.commit()
                        return result
                connection.commit()
            return True
        except Exception as e:
            print(f" Erreur SQL: {e}")
            return False

    def enable_pgvector(self) -> bool:
        """Activer l'extension pgvector"""
        print(" Activation de pgvector...")
        sql = "CREATE EXTENSION IF NOT EXISTS vector;"
        if self.run_query(sql):
            print(" pgvector activé")
            return True
        return False

    def check_current_type(self) -> str:
        """Vérifier le type actuel de la colonne embedding_of_text"""
        print(" Vérification du type de colonne actuel...")
        sql = """
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'project' 
            AND table_name = 'cards' 
            AND column_name = 'embedding_of_text';
        """
        result = self.run_query(sql, fetch_result=True)
        if result:
            current_type = result.get('data_type', 'unknown')
            print(f"   Type actuel: {current_type}")
            return current_type
        return None

    def modify_embedding_column(self) -> bool:
        """Modifier le type de colonne embedding_of_text"""
        print(" Modification de la colonne embedding_of_text...")
        
        # Vérifier d'abord si la colonne existe
        current_type = self.check_current_type()
        
        if current_type == 'USER-DEFINED':
            print("    La colonne est déjà de type vector")
            return True
        
        # Deux étapes : conversion du type
        sql = """
            ALTER TABLE project.cards 
            ALTER COLUMN embedding_of_text TYPE vector(1024) 
            USING embedding_of_text::vector;
        """
        
        if self.run_query(sql):
            print(" Colonne modifiée avec succès (FLOAT[] → vector(1024))")
            return True
        return False

    def create_index(self) -> bool:
        """Créer un index pour accélérer les recherches de similarité"""
        print(" Création d'un index IVFFlat pour accélérer les recherches...")
        
        # Index IVFFlat pour recherches approximatives rapides
        sql = """
            CREATE INDEX IF NOT EXISTS cards_embedding_idx 
            ON project.cards 
            USING ivfflat (embedding_of_text vector_cosine_ops)
            WITH (lists = 100);
        """
        
        if self.run_query(sql):
            print(" Index créé avec succès")
            return True
        return False

    def test_pgvector(self) -> bool:
        """Tester que pgvector fonctionne"""
        print(" Test de pgvector...")
        
        # Test 1: Distance entre vecteurs identiques (doit être 0)
        sql1 = "SELECT '[1,2,3]'::vector <=> '[1,2,3]'::vector AS distance;"
        result1 = self.run_query(sql1, fetch_result=True)
        
        if result1 and result1['distance'] == 0:
            print("   ✓ Test 1 réussi: distance entre vecteurs identiques = 0")
        else:
            print("   ✗ Test 1 échoué")
            return False
        
        # Test 2: Distance entre vecteurs différents (doit être > 0)
        sql2 = "SELECT '[1,2,3]'::vector <=> '[4,5,6]'::vector AS distance;"
        result2 = self.run_query(sql2, fetch_result=True)
        
        if result2 and result2['distance'] > 0:
            print(f"   ✓ Test 2 réussi: distance = {result2['distance']:.3f}")
        else:
            print("   ✗ Test 2 échoué")
            return False
        
        print(" pgvector fonctionne correctement")
        return True

    def setup(self):
        """Exécuter toute la configuration"""
        print("\n" + "=" * 60)
        print(" CONFIGURATION DE PGVECTOR")
        print("=" * 60 + "\n")

        steps = [
            ("Activation de l'extension", self.enable_pgvector),
            ("Modification du type de colonne", self.modify_embedding_column),
            ("Création de l'index", self.create_index),
            ("Tests", self.test_pgvector),
        ]

        for step_name, step_func in steps:
            if not step_func():
                print(f"\n Échec à l'étape: {step_name}")
                return False
            print()

        print("=" * 60)
        print(" CONFIGURATION PGVECTOR TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    dotenv.load_dotenv()
    setup = PgVectorSetup()
    setup.setup()

