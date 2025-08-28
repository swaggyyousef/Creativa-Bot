import sqlite3
import json
import logging
import os

DB_PATH = 'bot_database.db'

def get_connection():
    """Get SQLite database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    except Exception as e:
        logging.error(f"Error connecting to SQLite: {e}")
        return None

def execute_query(query, params=(), *, commit=True, fetch_one=False, fetch_all=False):
    """Execute a query on SQLite database."""
    conn = get_connection()
    if not conn:
        return None, 0
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        affected_rows = cursor.rowcount
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        if commit:
            conn.commit()
        
        return result, affected_rows
    except Exception as e:
        logging.error("Error executing SQLite query", exc_info=True)
        if commit:
            conn.rollback()
        return None, 0
    finally:
        conn.close()

def initialize_database():
    """Initialize SQLite database schema."""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faq (
                guild_id INTEGER PRIMARY KEY,
                qa TEXT DEFAULT '[]'
            )
        """)
        conn.commit()
        logging.info("SQLite database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing SQLite database: {e}")
    finally:
        conn.close()