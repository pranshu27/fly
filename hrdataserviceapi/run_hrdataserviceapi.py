from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import logging
from conn_mariadb import MariaDBDAO  # Replace your_module_name
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemas'))

# Swagger UI configuration
SWAGGER_URL = '/apidocs'
API_URL = '/schemas/swagger.json' #change back to this.

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "HR Data Service API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration (using your MariaDBDAO)
CONFIG_FILE = 'db.properties'
CONN_ID = 'my_mariadb'

def get_first_entrance_time(employee_id, date):
    """Retrieves the first entrance time from MariaDB."""
    query = """
        SELECT MIN(`timestamp`) AS first_entrance
        FROM `INOUT`.emp_inout_rec
        WHERE employee_id = %s AND DATE(`timestamp`) = %s AND in_out = 'IN'
    """
    params = (employee_id, date)

    try:
        with MariaDBDAO(CONFIG_FILE, CONN_ID) as db:
            result = db.execute_query(query, params)
            if result and result[0] and result[0][0]:
                return result[0][0].strftime('%Y-%m-%d %H:%M:%S')  # Format datetime
            else:
                return None
    except Exception as e:
        logging.error(f"Error retrieving first entrance time: {e}")
        return None

@app.route('/post/get_employee_entrance_first_in', methods=['POST'])
def get_employee_entrance():
    """API endpoint to get employee's first entrance time."""
    data = request.get_json()
    if not data or 'employee_id' not in data or 'date' not in data:
        return jsonify({'error': 'Missing employee_id or date'}), 400

    employee_id = data['employee_id']
    date = data['date']

    first_entrance = get_first_entrance_time(employee_id, date)

    if first_entrance:
        return jsonify({'first_entrance': first_entrance})
    else:
        return jsonify({'message': 'No entrance records found for the given employee and date'}), 404

if __name__ == '__main__':
    app.run(debug=True)