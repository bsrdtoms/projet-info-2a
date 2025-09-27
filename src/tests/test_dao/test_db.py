from utils.singleton import Singleton
from dao.db_connection import DBConnection


class TestDatabase:
    """
    Class for testing database queries
    """

    def run_and_print(self, sql_file: str = "data/request.sql"):
        print("🚀 Starting database query test")

        # 1. Load SQL from file
        with open(sql_file, encoding="utf-8") as f:
            sql_query = f.read()

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)

                    # 2. If the query has results, fetch them
                    if cursor.description:  # means the query returns rows
                        rows = cursor.fetchall()
                        print("📊 Query results:")
                        print(rows)
                    else:
                        print("✅ Query executed successfully (no result set).")

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

        print("🏁 Database query test completed")
        return True


if __name__ == "__main__":
    TestDatabase().run_and_print()
