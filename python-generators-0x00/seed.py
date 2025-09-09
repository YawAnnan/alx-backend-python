import mysql.connector
from mysql.connector import Error
import csv
import uuid

# --- Configuration ---
DB_HOST = 'localhost'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

# --- Prototypes ---

def connect_db():
    """Connects to the MySQL database server and returns a connection object."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Successfully connected to MySQL server.")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates the database ALX_prodev if it does not exist."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()

def connect_to_prodev():
    """Connects to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print(f"Successfully connected to database '{DB_NAME}'.")
        return connection
    except Error as e:
        print(f"Error connecting to database '{DB_NAME}': {e}")
        return None

def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(5, 2) NOT NULL
           """ )
        print(f"Table '{TABLE_NAME}' created or already exists.")
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()

def insert_data(connection, file_path):
    """Inserts data from a CSV file into the database if it does not exist."""
    cursor = connection.cursor()
    try:
        # Check if table is empty to avoid duplicate insertions on re-run
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = cursor.fetchone()[0]
        if count > 0:
            print("Data already exists in the table. Skipping insertion.")
            return

        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            data_to_insert = [
                (row[0], row[1], row[2], float(row[3])) for row in csv_reader
            ]

        sql = f"INSERT INTO {TABLE_NAME} (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, data_to_insert)
        connection.commit()
        print(f"Successfully inserted {cursor.rowcount} rows into '{TABLE_NAME}'.")
    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def stream_data_generator(connection):
    """A generator that streams rows from the database one by one."""
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        print("\nStreaming data from the database...")
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        for row in cursor:
            yield row
    except Error as e:
        print(f"Error streaming data: {e}")
    finally:
        cursor.close()

# --- Main execution logic ---
if __name__ == "__main__":
    initial_connection = None
    prodev_connection = None
    try:
        # Step 1: Connect to the MySQL server
        initial_connection = connect_db()
        if initial_connection is None:
            raise Exception("Failed to establish initial database connection.")

        # Step 2: Create the ALX_prodev database
        create_database(initial_connection)
        initial_connection.close()

        # Step 3: Connect to the newly created database
        prodev_connection = connect_to_prodev()
        if prodev_connection is None:
            raise Exception("Failed to connect to the ALX_prodev database.")

        # Step 4: Create the user_data table
        create_table(prodev_connection)

        # Step 5: Read and insert data from CSV
        insert_data(prodev_connection, 'user_data.csv')

        # Step 6: Demonstrate the data generator
        data_stream = stream_data_generator(prodev_connection)
        print("\n--- Streaming data from generator ---")
        for user in data_stream:
            print(user)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if prodev_connection and prodev_connection.is_connected():
            prodev_connection.close()
            print("\nMySQL connection closed.")
        if initial_connection and initial_connection.is_connected():
            initial_connection.close()
            print("Initial MySQL connection closed.")

