from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import random
import pymysql
import logging
from mariadb import MariaDBDAO  # Assuming your MariaDBDAO is in mariadb.py
import configparser

# DAG Configuration
CONFIG_FILE = "/opt/airflow/dags/db.properties"
CONN_ID = "my_mariadb"
TABLE_NAME = "emp_inout_rec"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 29),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': True,  # Enable catchup to run for past dates
}

def create_table_if_not_exists():
    """Creates the table if it does not exist."""
    try:
        with MariaDBDAO(CONFIG_FILE, CONN_ID) as dao:
            dao.execute_query(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    ingested_time DATETIME,
                    timestamp DATETIME,
                    employee_id INT,
                    employee_name VARCHAR(255),
                    factory VARCHAR(255),
                    in_out ENUM('IN', 'OUT'),
                    entrance VARCHAR(255),
                    door_number VARCHAR(50),
                    function VARCHAR(255),
                    division VARCHAR(255),
                    department VARCHAR(255),
                    section VARCHAR(255),
                    PRIMARY KEY (timestamp, employee_id, ingested_time)
                );
            """)
            logging.info(f"Table {TABLE_NAME} created (if it didn't exist).")
    except pymysql.MySQLError as e:
        logging.error(f"Error creating table: {e}")
    except Exception as e:
        logging.error(f"Failed to connect to MariaDB or other error: {e}")

def generate_dummy_data(execution_date):
    """Generates dummy data for a specific logical date (execution_date)."""
    ingested_time = datetime.now()
    timestamp = execution_date + timedelta(minutes=random.randint(0, 29))
    return {
        'ingested_time': ingested_time,
        'timestamp': timestamp,
        'emp_id': random.randint(1000, 9999),
        'employee_name': f"Employee{random.randint(1, 100)}",
        'factory': random.choice(["FactoryA", "FactoryB"]),
        'in_out': random.choice(['IN', 'OUT']),
        'entrance': random.choice(["Main", "Side"]),
        'door_number': str(random.randint(1, 10)),
        'function': random.choice(["IT"]),
        'division': random.choice(["BSID", "AAPD"]),
        'department': random.choice(["HRSD", "CAPD", "ML"]),
        'section': random.choice(["1", "2"]),
    }

def ingest_dummy_data(execution_date, **kwargs):
    logging.info(execution_date)
    """Ingests dummy data into the MariaDB table."""
    try:
        with MariaDBDAO(CONFIG_FILE, CONN_ID) as dao:
            num_rows = random.randint(5, 20)
            for i in range(num_rows):
                data = generate_dummy_data(execution_date)
                logging.info(data)
                query = f"""
                    INSERT INTO {TABLE_NAME} 
                    (ingested_time, timestamp, employee_id, employee_name, factory, in_out, entrance, door_number, function, division, department, section) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    data['ingested_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    data['emp_id'],
                    data['employee_name'],
                    data['factory'],
                    data['in_out'],
                    data['entrance'],
                    data['door_number'],
                    data['function'],
                    data['division'],
                    data['department'],
                    data['section'],
                )
                logging.info(f"Query: {query}")
                logging.info(f"Params: {params}")
                dao.execute_query(query, params)
            logging.info(f"Ingested {num_rows} rows of dummy data for {logical_date}.")
    except pymysql.MySQLError as e:
        logging.error(f"Error ingesting data: {e}")
    except Exception as e:
        logging.error(f"Failed to connect to MariaDB or other error: {e}")

# DAG Definition
with DAG(
    dag_id='inout_data_ingestion',
    default_args=default_args,
    schedule_interval='*/30 * * * *',
    catchup=True,  # Ensure all backlogs are processed
) as dag:

    create_table_task = PythonOperator(
        task_id='create_table',
        python_callable=create_table_if_not_exists,
    )

    # Using the execution_date from the context to pass to the ingest task
    ingest_task = PythonOperator(
        task_id='ingest_dummy_data',
        python_callable=ingest_dummy_data,
        op_kwargs={'execution_date': '{{ execution_date }}'},  # Automatically inject execution_date (logical date)
    )

create_table_task >> ingest_task
