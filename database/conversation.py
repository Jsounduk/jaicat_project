# database/conversation.py

import sqlite3
from datetime import datetime

class ConversationDatabase:
    def __init__(self, db_name='conversation_history.db'):
        """Initialize the database connection and create the table if it doesn't exist."""
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        """Create the conversation history table."""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')

    def add_conversation(self, user_input, assistant_response):
        """Add a conversation entry to the database."""
        timestamp = datetime.now().isoformat()
        with self.conn:
            self.conn.execute('''
                INSERT INTO conversations (user_input, assistant_response, timestamp)
                VALUES (?, ?, ?)
            ''', (user_input, assistant_response, timestamp))

    def get_conversation_history(self):
        """Retrieve the conversation history from the database."""
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM conversations ORDER BY timestamp')
            return cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()

if __name__ == "__main__":
    # Example usage
    db = ConversationDatabase()
    db.add_conversation("What's the weather today?", "It's sunny with a high of 25°C.")
    
    # Fetch all conversations
    history = db.get_conversation_history()
    for entry in history:
        print(f"User: {entry[1]} | Assistant: {entry[2]} | Time: {entry[3]}")
    
    db.close()
