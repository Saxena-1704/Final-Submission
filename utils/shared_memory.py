import sqlite3
from datetime import datetime

DB_FILE = "memory.db"

# Initialize DB and table
def _init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            file_key TEXT,
            key TEXT,
            value TEXT,
            timestamp TEXT,
            PRIMARY KEY (file_key, key)
        )
    """)
    conn.commit()
    conn.close()

# Save a key-value pair for a file
def save_to_memory(file_key, key, value):
    _init_db()
    timestamp = datetime.now().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memory (file_key, key, value, timestamp)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(file_key, key) DO UPDATE SET
            value = excluded.value,
            timestamp = excluded.timestamp
    """, (file_key, key, str(value), timestamp))
    conn.commit()
    conn.close()

# Get specific value
def get_from_memory(file_key, key):
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT value FROM memory WHERE file_key = ? AND key = ?
    """, (file_key, key))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Get full dictionary for a file_key
def get_full_memory(file_key):
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT key, value FROM memory WHERE file_key = ?
    """, (file_key,))
    rows = cursor.fetchall()
    conn.close()
    return {key: value for key, value in rows}

# Clear all memory
def clear_memory():
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memory")
    conn.commit()
    conn.close()

# Read entire DB
def read_memory():
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT file_key, key, value FROM memory
    """)
    rows = cursor.fetchall()
    conn.close()
    memory = {}
    for file_key, key, value in rows:
        if file_key not in memory:
            memory[file_key] = {}
        memory[file_key][key] = value
    return memory

# For testing
if __name__ == "__main__":
    save_to_memory("test_file.txt", "agent", "test_agent")
    save_to_memory("test_file.txt", "info", "Testing shared memory with SQLite")
    print("Full memory for test_file.txt:", get_full_memory("test_file.txt"))
    print("All memory data:", read_memory())
