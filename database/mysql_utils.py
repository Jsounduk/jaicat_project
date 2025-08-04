# database/mysql_utils.py

import mysql.connector
from mysql.connector import Error

class MySQLUtils:
    def __init__(self, host='localhost', database='jaicat_db', user='root', password=''):
        """Initialize MySQL connection."""
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """Establish connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print(f"Connected to MySQL database: {self.database}")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def execute_query(self, query, params=None):
        """Execute a query (INSERT, UPDATE, DELETE)."""
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.connection.commit()
                print("Query executed successfully.")
        except Error as e:
            print(f"Error executing query: {e}")
    
    def fetch_data(self, query, params=None):
        """Fetch data (SELECT queries)."""
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

    def close(self):
        """Close the MySQL database connection."""
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")
