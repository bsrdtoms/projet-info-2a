"""
Configuration script for pgvector in the database
To be executed only once after database creation

Usage:
    python src/setup_pgvector.py
"""

import os
import dotenv
from dao.db_connection import DBConnection


class PgVectorSetup:
    """Configure pgvector in the database"""

    def run_query(self, sql: str, fetch_result: bool = False):
        """Execute an SQL query"""
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
            print(f" SQL Error: {e}")
            return False

    def enable_pgvector(self) -> bool:
        """Enable the pgvector extension"""
        print(" Enabling pgvector...")
        sql = "CREATE EXTENSION IF NOT EXISTS vector;"
        if self.run_query(sql):
            print(" pgvector enabled")
            return True
        return False

    def check_current_type(self) -> str:
        """Check the current type of the embedding_of_text column"""
        print(" Checking current column type...")
        sql = """
            SELECT data_type
            FROM information_schema.columns
            WHERE table_schema = 'project'
            AND table_name = 'cards'
            AND column_name = 'embedding_of_text';
        """
        result = self.run_query(sql, fetch_result=True)
        if result:
            current_type = result.get("data_type", "unknown")
            print(f"   Current type: {current_type}")
            return current_type
        return None

    def modify_embedding_column(self) -> bool:
        """Modify the embedding_of_text column type"""
        print(" Modifying embedding_of_text column...")

        # First check if the column exists
        current_type = self.check_current_type()

        if current_type == "USER-DEFINED":
            print("    Column is already of vector type")
            return True

        # Two steps: type conversion
        sql = """
            ALTER TABLE project.cards
            ALTER COLUMN embedding_of_text TYPE vector(1024)
            USING embedding_of_text::vector;
        """

        if self.run_query(sql):
            print(" Column successfully modified (FLOAT[] → vector(1024))")
            return True
        return False

    def create_index(self) -> bool:
        """Create an index to speed up similarity searches"""
        print(" Creating IVFFlat index to speed up searches...")

        # IVFFlat index for fast approximate searches
        sql = """
            CREATE INDEX IF NOT EXISTS cards_embedding_idx
            ON project.cards
            USING ivfflat (embedding_of_text vector_cosine_ops)
            WITH (lists = 100);
        """

        if self.run_query(sql):
            print(" Index successfully created")
            return True
        return False

    def test_pgvector(self) -> bool:
        """Test that pgvector works"""
        print(" Testing pgvector...")

        # Test 1: Distance between identical vectors (should be 0)
        sql1 = "SELECT '[1,2,3]'::vector <=> '[1,2,3]'::vector AS distance;"
        result1 = self.run_query(sql1, fetch_result=True)

        if result1 and result1["distance"] == 0:
            print("   ✓ Test 1 passed: distance between identical vectors = 0")
        else:
            print("   ✗ Test 1 failed")
            return False

        # Test 2: Distance between different vectors (should be > 0)
        sql2 = "SELECT '[1,2,3]'::vector <=> '[4,5,6]'::vector AS distance;"
        result2 = self.run_query(sql2, fetch_result=True)

        if result2 and result2["distance"] > 0:
            print(f"   ✓ Test 2 passed: distance = {result2['distance']:.3f}")
        else:
            print("   ✗ Test 2 failed")
            return False

        print(" pgvector is working correctly")
        return True

    def setup(self):
        """Execute the entire configuration"""
        print("\n" + "=" * 60)
        print(" PGVECTOR CONFIGURATION")
        print("=" * 60 + "\n")

        steps = [
            ("Extension activation", self.enable_pgvector),
            ("Column type modification", self.modify_embedding_column),
            ("Index creation", self.create_index),
            ("Tests", self.test_pgvector),
        ]

        for step_name, step_func in steps:
            if not step_func():
                print(f"\n Failed at step: {step_name}")
                return False
            print()

        print("=" * 60)
        print(" PGVECTOR CONFIGURATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True


# If the application is used as defined in the README, this code will never run
if __name__ == "__main__":
    dotenv.load_dotenv()
    setup = PgVectorSetup()
    setup.setup()