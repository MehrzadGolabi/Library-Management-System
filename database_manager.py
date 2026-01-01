import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(
    filename='library_system.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BaseEntity:
    _pool = None

    def __init__(self):
        self._initialize_pool()

    @classmethod
    def _initialize_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="lib_pool",
                    pool_size=5,
                    host=os.getenv('MYSQL_HOST', 'localhost'),
                    port=int(os.getenv('MYSQL_PORT', 3306)),
                    database=os.getenv('MYSQL_DATABASE'),
                    user=os.getenv('MYSQL_USER'),
                    password=os.getenv('MYSQL_PASSWORD')
                )
            except mysql.connector.Error as err:
                logging.error(f"Error creating connection pool: {err}")
                raise

    def _get_connection(self):
        return self._pool.get_connection()

    def execute_query(self, sql, params=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            logging.error(f"Error executing query: {err}\nSQL: {sql}\nParams: {params}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def fetch_data(self, sql, params=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(f"Error fetching data: {err}\nSQL: {sql}\nParams: {params}")
            raise
        finally:
            cursor.close()
            conn.close()