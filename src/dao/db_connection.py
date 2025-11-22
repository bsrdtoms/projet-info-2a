import os
import dotenv
import psycopg2

from psycopg2.extras import RealDictCursor
from utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """
    Database connection class
    It allows opening only one single connection
    """

    def __init__(self):
        """Opens the connection"""
        dotenv.load_dotenv()  # loads variables from .env

        self.__connection = psycopg2.connect(
            host=os.environ["PGHOST"],
            port=os.environ["PGPORT"],
            database=os.environ["PGDATABASE"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        return self.__connection
