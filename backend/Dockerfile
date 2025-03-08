FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create the instance directory for the SQLite database
RUN mkdir -p instance

# Expose the port the API runs on
EXPOSE 5000

# Command to run the API
CMD ["python", "app.py"]
