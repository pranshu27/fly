FROM apache/airflow:2.8.2

# Copy the requirements file into the container
COPY requirements.txt /requirements.txt

# Install the dependencies
RUN pip install -r /requirements.txt

# # Copy any other files, for example, your mariadb.py file.
# COPY mariadb.py /opt/airflow/mariadb.py