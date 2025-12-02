# Use lightweight Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system packages required for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirement list 
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]
