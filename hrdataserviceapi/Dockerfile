# Use a Python base image (adjust version as needed)
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port your Flask app will run on (default is 5000)
EXPOSE 5000

# Set the command to run your Flask application
CMD ["python", "app.py"]