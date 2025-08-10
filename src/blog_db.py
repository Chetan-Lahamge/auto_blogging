import sqlite3
import logging
import os
from .config import DATABASE_NAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db():
    conn = None
    try:
        os.makedirs(os.path.dirname(DATABASE_NAME), exist_ok=True)
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL
            )
        """)
        conn.commit()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def add_blog_entry(title: str, status: str = "posted"):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO blogs (title, status) VALUES (?, ?)", (title, status))
        conn.commit()
        logging.info(f"Added blog entry: {title} with status {status}")
    except sqlite3.IntegrityError:
        logging.warning(f"Blog entry with title '{title}' already exists in DB. Skipping addition.")
    except sqlite3.Error as e:
        logging.error(f"Error adding blog entry '{title}': {e}")
    finally:
        if conn:
            conn.close()

def blog_exists(title: str) -> bool:
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM blogs WHERE title = ?", (title,))
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logging.error(f"Error checking for blog entry '{title}': {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_recent_topics(limit: int = 5) -> list[str]:
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM blogs ORDER BY id DESC LIMIT ?", (limit,))
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Error retrieving recent topics: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_normalized_titles() -> list[str]:
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM blogs")
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Error retrieving all normalized titles: {e}")
        return []
    finally:
        if conn:
            conn.close()
