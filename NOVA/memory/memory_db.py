import sqlite3
import datetime
import os
import sys
import re

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        MEMORY_DB_PATH = "data/nova_memory.db"
        MEMORY_ENABLED = True
        MEMORY_MAX_RECENT = 10

def scrub_sensitive_text(text: str) -> str:
    """Redacts common sensitive patterns like emails and long tokens."""
    if not text:
        return text
    
    # Redact Emails
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[REDACTED_EMAIL]', text)
    
    # Redact potential API keys / Long tokens (32+ alphanumeric chars)
    text = re.sub(r'\b[a-zA-Z0-9]{32,}\b', '[REDACTED_TOKEN]', text)
    
    # Redact phone numbers (simple pattern: 10+ digits)
    text = re.sub(r'\b\d{10,}\b', '[REDACTED_PHONE]', text)
    
    return text

def get_connection():
    """Returns a connection to the SQLite database."""
    if not config.MEMORY_ENABLED:
        return None
    try:
        conn = sqlite3.connect(config.MEMORY_DB_PATH)
        return conn
    except Exception as e:
        print(f"Error connecting to memory database: {e}")
        return None

def initialize_memory():
    """Initializes the database and creates tables if they don't exist."""
    if not config.MEMORY_ENABLED:
        return

    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        # Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_command TEXT,
                nova_response TEXT,
                intent TEXT,
                success INTEGER
            )
        ''')
        
        # Preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Error initializing memory database: {e}")
    finally:
        conn.close()

def save_interaction(user_command, nova_response, intent="unknown", success=True):
    """Saves a scrubbed interaction to the database."""
    if not config.MEMORY_ENABLED:
        return

    user_command = scrub_sensitive_text(user_command)
    nova_response = scrub_sensitive_text(nova_response)

    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO interactions (timestamp, user_command, nova_response, intent, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.datetime.now().isoformat(), user_command, nova_response, intent, 1 if success else 0))
        conn.commit()
    except Exception as e:
        print(f"Error saving interaction: {e}")
    finally:
        conn.close()

def get_recent_interactions(limit=None):
    """Retrieves recent interactions from the database."""
    if not config.MEMORY_ENABLED:
        return []

    limit = limit or config.MEMORY_MAX_RECENT
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, user_command, nova_response, intent FROM interactions ORDER BY id DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving interactions: {e}")
        return []
    finally:
        conn.close()

def set_preference(key, value):
    """Sets a user preference."""
    if not config.MEMORY_ENABLED:
        return

    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"Error saving preference: {e}")
    finally:
        conn.close()

def get_preference(key, default=None):
    """Retrieves a user preference."""
    if not config.MEMORY_ENABLED:
        return default

    conn = get_connection()
    if not conn:
        return default

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row[0] if row else default
    except Exception as e:
        print(f"Error retrieving preference: {e}")
        return default
    finally:
        conn.close()

def delete_preference(key):
    """Deletes a user preference."""
    if not config.MEMORY_ENABLED:
        return

    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM preferences WHERE key = ?', (key,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting preference: {e}")
    finally:
        conn.close()

def clear_interactions():
    """Clears interaction history."""
    if not config.MEMORY_ENABLED:
        return

    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM interactions')
        conn.commit()
    except Exception as e:
        print(f"Error clearing interactions: {e}")
    finally:
        conn.close()
