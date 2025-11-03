import mysql.connector
from mysql.connector import errorcode
import csv
import uuid

# --- Database connection setup ---
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sudoAdmin@2025"  # update this with your actual MySQL password
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
    finally:
        cursor.close()


def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sudoAdmin@2025",  # update this as well
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None


# --- Table setup ---
def create_table(connection):
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX (user_id)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        cursor.close()


# --- Insert data (auto-generate user_id) ---
def insert_data(connection, csv_file):
    try:
        cursor = connection.cursor()
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file,delimiter=',')
            for row in reader:
                name = row["name"]
                email = row["email"]
                age = row["age"]
                user_id = str(uuid.uuid4())  # auto-generate unique ID
                insert_query = """
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (user_id, name, email, age))
        connection.commit()
        print("Data inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
    except FileNotFoundError:
        print("CSV file not found.")
    finally:
        cursor.close()
