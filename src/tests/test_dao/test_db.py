from dao.db_connection import get_connection  # ou DBConnection si tu utilises la classe

if __name__ == "__main__":
    # version simple si tu as défini get_connection()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(cur.fetchone())
    conn.close()

    # version classe avec Singleton
    # db = DBConnection()
    # conn = db.connection
    # cur = conn.cursor()
    # cur.execute("SELECT version();")
    # print(cur.fetchone())
