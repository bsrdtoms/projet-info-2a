import os
import dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

dotenv.load_dotenv()  # charge les variables depuis .env

def get_connection():
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        database=os.environ["POSTGRES_DATABASE"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
        cursor_factory=RealDictCursor,
    )
    return conn
