import sqlite3
import functools


conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
""")

# Insert sample records
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("John Ametepe", "johnametepe@example.com"))
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Jane togo", "janetogo@example.com"))

conn.commit()
conn.close()

print("Database and sample users created!")

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")  # Open DB connection
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()  # Always close connection
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()          # Commit on success
            return result
        except Exception as e:
            conn.rollback()        # Rollback on error
            raise e
    return wrapper

# Fetch user by ID with automatic connection handling
# user = get_user_by_id(user_id=1)
# print(user)
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?",
        (new_email, user_id)
    )

# Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
user = get_user_by_id(user_id=1)
print(user)