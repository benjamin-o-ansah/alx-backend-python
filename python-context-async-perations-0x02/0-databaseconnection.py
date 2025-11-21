import sqlite3


import sqlite3

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
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("John Doe", "john@example.com"))
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Jane Smith", "jane@example.com"))

conn.commit()
conn.close()

print("Database and sample users created!")

# ---------------------------
# Class-based context manager
# ---------------------------
class DatabaseConnection:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def __enter__(self):
        # Open the database connection
        self.conn = sqlite3.connect(self.db_file)
        return self.conn  # this is assigned to the "as" variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection automatically
        if self.conn:
            if exc_type:
                # Optional: Rollback if an exception occurred
                self.conn.rollback()
            else:
                # Commit if no exception
                self.conn.commit()
            self.conn.close()
        # Returning False propagates exceptions if any
        return False


# ---------------------------
# Using the context manager
# ---------------------------
with DatabaseConnection("users.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print("Users in the database:")
    for row in results:
        print(row)
