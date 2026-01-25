import sqlite3
import numpy as np
import json
import os

DB_PATH = "privacy_shield.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authorized_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            embedding TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_embedding(embedding):
    """Saves a numpy array embedding as a JSON string in SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Clear existing authorized user (Single user mode)
    cursor.execute('DELETE FROM authorized_user')
    
    embedding_json = json.dumps(embedding.tolist())
    cursor.execute('INSERT INTO authorized_user (embedding) VALUES (?)', (embedding_json,))
    conn.commit()
    conn.close()

def get_authorized_embedding():
    """Retrieves the stored embedding and returns it as a numpy array."""
    if not os.path.exists(DB_PATH):
        return None
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT embedding FROM authorized_user LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return np.array(json.loads(row[0]))
    return None

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
