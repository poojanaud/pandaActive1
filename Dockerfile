FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8080

# Make the startup script executable
RUN chmod +x /app/start.sh

# Use the startup script
CMD ["/app/start.sh"]