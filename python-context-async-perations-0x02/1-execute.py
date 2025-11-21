import sqlite3

# ---------------------------
# Class-based context manager
# ---------------------------

# conn = sqlite3.connect("users.db")
# cursor = conn.cursor()

# # 1. Add the 'age' column if it doesn't exist
# cursor.execute("""
# ALTER TABLE users
# ADD COLUMN age INTEGER
# """)

# # Note: If the column already exists, SQLite will raise an error.
# # If needed, wrap in try/except to ignore that.

# # 2. Update existing users with their ages
# # Example: assume user IDs 1, 2, 3...
# user_ages = {
#     1: 30,  # John Doe
#     2: 22,  # Jane Doe
#     3: 27   # Example for more users
# }

# for user_id, age in user_ages.items():
#     cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, user_id))

# # Commit changes and close connection
# conn.commit()
# conn.close()

# print("Users table updated with age column and values.")

class ExecuteQuery:
    def __init__(self, db_file, query, params=None):
        """
        db_file: path to SQLite database
        query: SQL query string
        params: tuple of parameters for the query (optional)
        """
        self.db_file = db_file
        self.query = query
        self.params = params or ()
        self.conn = None
        self.result = None

    def __enter__(self):
        # Open the database connection
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        
        # Execute the query with parameters
        cursor.execute(self.query, self.params)
        
        # Fetch all results
        self.result = cursor.fetchall()
        
        # Return the result to the "as" variable
        return self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Commit/rollback if needed
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
        # Do not suppress exceptions
        return False

# ---------------------------
# Using the context manager
# ---------------------------

query = "SELECT * FROM users WHERE age < ?"
params = (25,)

with ExecuteQuery("users.db", query, params) as results:
    print("Users older than 25:")
    for row in results:
        print (row)
