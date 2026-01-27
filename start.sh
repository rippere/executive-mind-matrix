#!/bin/bash
# Quick start script for Executive Mind Matrix

echo "🧠 Executive Mind Matrix - Starting..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your actual API keys and database IDs"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container"
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
else
    echo "💻 Running locally"

    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate venv
    source venv/bin/activate

    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt

    # Run the application
    echo "🚀 Starting server on http://localhost:8000"
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
fi
