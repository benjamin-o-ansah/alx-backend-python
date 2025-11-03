# alx-backend-python
# Python MySQL Data Seeding Scripts

This project provides a set of Python scripts to automatically set up a MySQL database, create a table, and populate it with data from a CSV file. It's designed to streamline the initial data loading process for development and testing environments.

## Overview

The solution consists of two main Python files:

-   `seed.py`: A module containing all the necessary functions for database and table creation, connection handling, and data insertion.
-   `main.py`: The main executable script that orchestrates the entire process by calling the functions from `seed.py`.

The scripts will perform the following actions:
1.  Connect to a local MySQL server.
2.  Create a new database named `ALX_prodev` if it doesn't already exist.
3.  Create a table named `user_data` within the `ALX_prodev` database.
4.  Read data from a `user_data.csv` file.
5.  Generate a unique UUID for each user record.
6.  Insert the records into the `user_data` table.
7.  Perform a simple verification by printing the first 5 records from the table.

---

## Prerequisites

Before you begin, ensure you have the following installed and running:

-   Python 3.6+
-   MySQL Server
-   The `mysql-connector-python` library for Python.

You can install the required Python library using pip:
```bash
pip install mysql-connector-python
```

---

## Setup

1.  **Clone the Repository**
    Clone or download this repository to your local machine.

2.  **Update Database Credentials**
    You **must** update the MySQL password in the `seed.py` file. Open `seed.py` and replace `"your_password"` with your actual MySQL root password in the following functions:
    -   `connect_db()`
    -   `connect_to_prodev()`

    **Example (in `seed.py`):**
    ```python
    # Before
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password" # update this
    )
    
    # After
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySecretPassword123" # updated
    )
    ```

3.  **Create the CSV Data File**
    In the same directory as the Python scripts, create a file named `user_data.csv`. The file must have the following headers: `name`, `email`, and `age`.

    **`user_data.csv` example:**
    ```csv
    name,email,age
    Alice Johnson,alice.j@example.com,28
    Bob Smith,bob.smith@example.com,34.5
    Charlie Brown,charlie.b@example.com,22
    Diana Prince,diana.p@example.com,3000
    Eve Adams,eve.a@example.com,45
    Frank White,frank.w@example.com,52
    ```

---

## Usage

Once the setup is complete, you can run the main script from your terminal:

```bash
python main.py
```

The script will execute all the steps and print status messages to the console.

### Expected Output

If the script runs successfully, you should see output similar to this:

```
Database ALX_prodev created or already exists.
Connection successful
Table user_data created or already exists.
Data inserted successfully.
Database ALX_prodev is present
[('uuid-string-1', 'Alice Johnson', 'alice.j@example.com', Decimal('28.00')), ('uuid-string-2', 'Bob Smith', 'bob.smith@example.com', Decimal('34.50')), ('uuid-string-3', 'Charlie Brown', 'charlie.b@example.com', Decimal('22.00')), ('uuid-string-4', 'Diana Prince', 'diana.p@example.com', Decimal('3000.00')), ('uuid-string-5', 'Eve Adams', 'eve.a@example.com', Decimal('45.00'))]
```
*Note: The `uuid-string` will be a unique, auto-generated UUID for each record.*

---

## Database Schema

The script creates a single table, `user_data`, with the following structure:

| Column  | Type         | Constraints   | Description                                 |
| :------ | :----------- | :------------ | :------------------------------------------ |
| user_id | `CHAR(36)`   | `PRIMARY KEY` | A unique identifier (UUID) for each user.   |
| name    | `VARCHAR(255)`| `NOT NULL`    | The name of the user.                       |
| email   | `VARCHAR(255)`| `NOT NULL`    | The user's email address.                   |
| age     | `DECIMAL(5,2)`| `NOT NULL`    | The age of the user.                        |

An index is also created on the `user_id` column to improve query performance.