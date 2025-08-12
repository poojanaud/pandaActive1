#!/bin/sh
# Wait for any dependencies to be ready
echo "Starting PandaAI API..."

# Set the port
export PORT=${PORT:-8080}

# Start the application
echo "Starting uvicorn on port $PORT"
exec uvicorn app:app --host 0.0.0.0 --port $PORT --reload