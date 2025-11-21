import asyncio
import aiosqlite

# ---------------------------
# Asynchronous fetch all users
# ---------------------------
async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            print("All users:")
            for row in users:
                print(row)
            return users

# ---------------------------
# Asynchronous fetch users older than 40
# ---------------------------
async def async_fetch_older_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            older_users = await cursor.fetchall()
            print("Users older than 40:")
            for row in older_users:
                print(row)
            return older_users

# ---------------------------
# Run both queries concurrently
# ---------------------------
async def fetch_concurrently():
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    all_users, older_users = results
    # Optional: do something with results
    print(f"Fetched {len(all_users)} users in total.")
    print(f"{len(older_users)} users are older than 40.")

# ---------------------------
# Execute
# ---------------------------
asyncio.run(fetch_concurrently())
