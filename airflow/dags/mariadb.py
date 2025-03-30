import pymysql
import os
import configparser

class MariaDBDAO:
    """A Data Access Object (DAO) for MariaDB using a local properties file and environment variable for password."""

    def __init__(self, config_file, conn_id):
        """
        Initializes the MariaDBDAO using a local properties file and environment variable.

        Args:
            config_file (str): Path to the properties file.
            conn_id (str): Section name in the properties file for connection details.
        """
        self.config_file = config_file
        self.conn_id = conn_id
        self.connection = None

        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        if conn_id not in self.config:
            raise ValueError(f"Connection ID '{conn_id}' not found in configuration file.")

        self.host = self.config[conn_id]['host']
        self.user = self.config[conn_id]['user']
        self.database = self.config[conn_id]['database']
        self.port = int(self.config[conn_id].get('port', 3306))  # Default port

        # self.password = os.environ.get(f"{conn_id.upper()}_PASSWORD")
        self.password="joker777"

        if self.password is None:
            raise ValueError(f"Environment variable {conn_id.upper()}_PASSWORD not set.")

    def connect(self):
        """Establishes a connection to the MariaDB database."""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print(f"Successfully connected to MariaDB: {self.database} on {self.host}:{self.port}")
            return True
        except pymysql.MySQLError as e:
            print(f"Error connecting to MariaDB: {e}")
            return False

    def execute_query(self, query, params=None):
        """Executes a SQL query and returns the result (if any)."""
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(query, params)
                    self.connection.commit()
                    if query.lower().startswith('select'):
                        return cursor.fetchall()
                    else:
                        return None
            except pymysql.MySQLError as e:
                print(f"Error executing query: {e}")
                self.connection.rollback()
                return None
        else:
            print("No database connection available.")
            return None

    def close(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            print("MariaDB connection closed.")
            self.connection = None
