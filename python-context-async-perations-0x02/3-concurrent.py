#!/usr/bin/env python3
import asyncio
import aiosqlite


async def setup_db():
    """Create users table with sample data if not exists"""
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                age INTEGER
            )
        """)
        await db.execute("INSERT OR IGNORE INTO users (id, name, email, age) VALUES (1, 'Alice', 'alice@example.com', 30)")
        await db.execute("INSERT OR IGNORE INTO users (id, name, email, age) VALUES (2, 'Bob', 'bob@example.com', 22)")
        await db.execute("INSERT OR IGNORE INTO users (id, name, email, age) VALUES (3, 'Charlie', 'charlie@example.com', 45)")
        await db.execute("INSERT OR IGNORE INTO users (id, name, email, age) VALUES (4, 'Diana', 'diana@example.com', 55)")
        await db.commit()


async def async_fetch_users():
    """Fetch all users"""
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()


async def async_fetch_older_users():
    """Fetch users older than 40"""
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()


async def fetch_concurrently():
    """Run both queries concurrently"""
    await setup_db()
    users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    print("All users:")
    for u in users:
        print(u)

    print("\nUsers older than 40:")
    for u in older_users:
        print(u)


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
