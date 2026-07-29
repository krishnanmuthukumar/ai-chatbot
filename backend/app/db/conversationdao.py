import app.db.database as db

def insert_message(self, role: str):
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (self.conversation_id, role, self.message)
        )
        conn.commit()

def create_conversation(self):
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (user_id) VALUES (?)",
            (1,)  # Assuming a default user_id for demonstration
        )
        conn.commit()

def get_last_conversation_id(self):
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]

def get_conversation_history(conversation_id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,)
    )
    return cursor.fetchall()

def getMessagesCount(conversaion_id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM messages WHERE conversation_id = ? ", (conversaion_id,)
    )
    return cursor.fetchone()[0]