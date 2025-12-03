#!/bin/bash
# Development startup script for ARL Backend

set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate log file with timestamp
LOG_FILE="logs/dev-$(date +%Y%m%d-%H%M%S).log"

# Print log file location
echo "📝 Logging to: $LOG_FILE"
echo ""

# Function to log and print
log_and_print() {
    tee -a "$LOG_FILE"
}

echo "🚀 Starting ARL Backend Development Environment" | log_and_print
echo "" | log_and_print

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first:" | log_and_print
    echo "   sudo systemctl start docker" | log_and_print
    exit 1
fi

echo "✅ Docker is running" | log_and_print
echo "" | log_and_print

# Start Docker services
echo "📦 Starting PostgreSQL and Redis..." | log_and_print
docker compose up -d 2>&1 | log_and_print

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..." | log_and_print
sleep 3

# Check if services are healthy
if docker compose ps | grep -q "healthy"; then
    echo "✅ Services are healthy" | log_and_print
else
    echo "⚠️  Services starting... checking again in 5 seconds" | log_and_print
    sleep 5
fi

echo "" | log_and_print

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..." | log_and_print
    uv sync 2>&1 | log_and_print
else
    echo "✅ Virtual environment exists" | log_and_print
fi

echo "" | log_and_print

# Run migrations
echo "🔄 Running database migrations..." | log_and_print
.venv/bin/alembic upgrade head 2>&1 | log_and_print

echo "" | log_and_print
echo "✅ Setup complete!" | log_and_print
echo "" | log_and_print
echo "🌟 Starting backend server..." | log_and_print
echo "   API: http://localhost:8000" | log_and_print
echo "   Docs: http://localhost:8000/api/v1/docs" | log_and_print
echo "   Health: http://localhost:8000/health" | log_and_print
echo "" | log_and_print

# Start backend (with logging)
.venv/bin/uvicorn app.main:app --reload 2>&1 | log_and_print
