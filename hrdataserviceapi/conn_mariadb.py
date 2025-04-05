import pymysql
import configparser
import logging

class MariaDBDAO:
    # ... (rest of your class)
    def __init__(self, config_file, conn_id):
        """Initializes the MariaDBDAO."""
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
        self.port = int(self.config[conn_id].get('port', 3306))
        self.password = self.config[conn_id]['password']

    def connect(self):
        """Establishes a connection to the MariaDB database."""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connect_timeout=5
            )
            logging.info(f"Successfully connected to MariaDB: {self.database} on {self.host}:{self.port}")
            return True
        except pymysql.MySQLError as e:
            logging.error(f"Error connecting to MariaDB: {e}")
            return False
        except Exception as e:
            logging.error(f"General error connecting to MariaDB: {e}")
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
                logging.error(f"Error executing query: {e}")
                self.connection.rollback()
                return None
            except Exception as e:
                logging.error(f"General error executing query: {e}")
                self.connection.rollback()
                return None
        else:
            logging.error("No database connection available.")
            return None

    def close(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            logging.info("MariaDB connection closed.")
            self.connection = None

    def __enter__(self):
        """Context manager entry."""
        if not self.connect():
            raise Exception("Failed to connect to database.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        self.close()