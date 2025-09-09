#!/usr/bin/env python3
import sqlite3


class ExecuteQuery:
    """Context manager to execute a query and return results"""

    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params if params else ()
        self.conn = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute(self.query, self.params)
        self.results = cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f"An error occurred: {exc_value}")
        if self.conn:
            self.conn.close()
        return False


def setup_db():
    """Ensure the users table exists with age column and sample data"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Drop old table and recreate (ensures correct schema for ALX task)
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            age INTEGER
        )
    """)

    # Insert fresh sample users
    cursor.execute("INSERT INTO users (id, name, email, age) VALUES (1, 'Alice', 'alice@example.com', 30)")
    cursor.execute("INSERT INTO users (id, name, email, age) VALUES (2, 'Bob', 'bob@example.com', 22)")
    cursor.execute("INSERT INTO users (id, name, email, age) VALUES (3, 'Charlie', 'charlie@example.com', 28)")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_db()

    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery("users.db", query, params) as results:
        print("Users older than 25:")
        for row in results:
            print(row)
    print("Exited context manager.")    
    print("Database connection closed.")