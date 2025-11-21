"""
Script to initialize user and history tables

Usage:
    python src/utils/init_users_tables.py
"""

from dao.db_connection import DBConnection
import os


def run_sql_file(filepath: str) -> bool:
    """Execute an SQL file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()

        print(f"✅ SQL file executed: {filepath}")
        return True

    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("🚀 USER TABLES INITIALIZATION")
    print("=" * 60 + "\n")

    sql_file = "data/add_users_tables.sql"

    if not os.path.exists(sql_file):
        print(f"❌ File not found: {sql_file}")
        print("   Create the SQL file with the tables first")
        return

    # Execute the SQL file
    if run_sql_file(sql_file):
        print("\n" + "=" * 60)
        print("✅ TABLES SUCCESSFULLY CREATED")
        print("=" * 60)
        print("\nCreated tables:")
        print("  ✓ project.users")
        print("  ✓ project.sessions")
        print("  ✓ project.favorites")
        print("  ✓ project.search_history")
        print("\nDefault admin account:")
        print("  Email: admin@magicsearch.com")
        print("  Password: our very secure password")
    else:
        print("\n❌ Initialization failed")


if __name__ == "__main__":
    main()