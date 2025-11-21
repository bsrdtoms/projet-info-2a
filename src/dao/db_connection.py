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
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        return self.__connection
