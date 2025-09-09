#!/usr/bin/env python3
import sqlite3


class DatabaseConnection:
    """Custom class-based context manager for database connections"""

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        # open connection when entering context
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f"An error occurred: {exc_value}")
        if self.conn:
            self.conn.close()
        return False


def setup_db():
    """Ensure the users table exists with some sample data"""
    with DatabaseConnection("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
        cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
        conn.commit()


if __name__ == "__main__":
    setup_db()

    with DatabaseConnection("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(results)
    print("Database connection closed.")    
    print("Exited context manager.")