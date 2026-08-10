import sqlite3

_connection = None

def init_db(db_name = "chatapp.db"):
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(db_name, check_same_thread=False)
        cursor = _connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                title_generated BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        print(f"Database initialized with {db_name}")

def get_db_connection():
    if _connection is None:
        raise Exception("Database not initialized.")
    return _connection
def close_db_connection():
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
        print("Database connection closed.")
