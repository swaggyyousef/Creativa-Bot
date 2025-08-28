7import logging
import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

load_dotenv()

# Render provides DATABASE_URL automatically
DATABASE_URL = os.getenv('DATABASE_URL')

# Fallback to individual variables if needed
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': os.getenv('DB_PORT', '5432')
}

def execute_query(query, params=(), *, commit=True, fetch_one=False, fetch_all=False, database=None, user=None, password=None):
    db = get_connection(database=database, user=user, password=password)
    if not db:
        return None
    try:
        with db.cursor() as cursor:
            cursor.execute(query, params)
            affected_rows = cursor.rowcount  # Capture the number of affected rows
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            if commit:
                db.commit()
            return result, affected_rows  # Return both the result and affected rows
    except Exception as e:
        logging.error("Error executing query", exc_info=True)
        if commit:
            db.rollback()
        return None, 0  # Return 0 affected rows in case of error
    finally:
        db.close()

def get_connection(database=None, user=None, password=None, use_database=True):
    """Establish and return a database connection."""
    try:
        # Use DATABASE_URL if available (Render provides this)
        if DATABASE_URL:
            connection = psycopg2.connect(DATABASE_URL)
            return connection
        
        # Fallback to individual config
        config = DB_CONFIG.copy()
        if database:
            config["database"] = database
        if user:
            config["user"] = user
        if password:
            config["password"] = password
        if not use_database:
            config.pop('database', None)
        
        connection = psycopg2.connect(**config)
        return connection
    except Error as e:
        logging.error(f"Error connecting to PostgreSQL: {e}")
        return None
        
def initialize_database():
    """Initialize the database schema."""
    db = get_connection()
    if not db:
        return
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faq (
                    guild_id BIGINT PRIMARY KEY,
                    qa JSONB DEFAULT '[]'
                )
            """)
            db.commit()
    except Error as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        db.close()