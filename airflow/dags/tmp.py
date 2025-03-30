from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import random
import pymysql
from mariadb import MariaDBDAO  # Assuming your DAO is in my_mariadb_dao.py

# Replace with the actual path to your properties file and connection ID
CONFIG_FILE = "db.properties"
CONN_ID = "my_mariadb"
TABLE_NAME = "emp_inout_rec"  # Table name


def create_table_if_not_exists():
    """Creates the table if it does not exist."""
    dao = MariaDBDAO(CONFIG_FILE, CONN_ID)
    if dao.connect():
        try:
            dao.execute_query(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    timestamp DATETIME,
                    emp_id INT,
                    in_out VARCHAR(10)
                )
            """)
            print(f"Table {TABLE_NAME} created (if it didn't exist).")
        except pymysql.MySQLError as e:
            print(f"Error creating table: {e}")
        dao.close()
    else:
        print("Failed to connect to MariaDB.")

def generate_dummy_data():
    """Generates a single row of dummy data."""
    return {
        'timestamp': datetime.now(),
        'emp_id': random.randint(1000, 9999),
        'in_out': random.choice(['IN', 'OUT']),
    }

def ingest_dummy_data():
    """Ingests dummy data into the MariaDB table."""
    dao = MariaDBDAO(CONFIG_FILE, CONN_ID)
    if dao.connect():
        data = generate_dummy_data()
        try:
            dao.execute_query(
                f"INSERT INTO {TABLE_NAME} (timestamp, emp_id, in_out) VALUES (%s, %s, %s)",
                (data['timestamp'], data['emp_id'], data['in_out']),
            )
            print(f"Ingested dummy data: {data}")
        except pymysql.MySQLError as e:
            print(f"Error ingesting data: {e}")

        dao.close()
    else:
        print("Failed to connect to MariaDB.")

create_table_if_not_exists()