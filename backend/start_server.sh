#!/bin/bash

# Load environment variables from .env file
source /app/backend/.env

# Change to backend directory
cd /app/backend

# Start uvicorn server
/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 --reload