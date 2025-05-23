#!/bin/bash

# Create a simple script to run the FastAPI server for testing

echo "Starting Khoj Backend API server for testing..."
echo "This will install requirements and start the server on port 8000"

# Install requirements
pip install -r requirements.txt

# Set environment variable for auth bypass
export AUTH_BYPASS_ENABLED=true

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
