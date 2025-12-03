# ARL Backend Setup Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- uv package manager

## Quick Start

### Option 1: Automated Startup (Recommended)

```bash
cd arl-backend

# Ensure Docker is running
sudo systemctl start docker

# Run startup script (handles everything)
./start-dev.sh
```

The script will:
- Start PostgreSQL and Redis containers
- Install dependencies if needed
- Run database migrations
- Start the backend server

### Option 2: Manual Setup

#### 1. Start Docker Services

First, ensure Docker daemon is running:

```bash
# Start Docker daemon (requires sudo)
sudo systemctl start docker

# Or on macOS
# Docker Desktop should be running
```

Then start PostgreSQL and Redis:

```bash
cd arl-backend
docker compose up -d
```

Verify services are running:

```bash
docker compose ps
```

#### 2. Install Dependencies

```bash
# Install Python dependencies
uv sync
```

#### 3. Run Database Migrations

```bash
# Apply database schema
.venv/bin/alembic upgrade head
```

#### 4. Start Backend

```bash
# Development mode with auto-reload
.venv/bin/uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

- API Docs: http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/health

## Environment Configuration

The `.env` file contains the configuration:

```env
# Database
DATABASE_URL=postgresql://arl_user:arl_dev_password@localhost:5432/arl_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production-CHANGE-THIS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

## Docker Services Management

### Start services
```bash
docker compose up -d
```

### Stop services
```bash
docker compose down
```

### View logs
```bash
docker compose logs -f
```

### Restart services
```bash
docker compose restart
```

## Troubleshooting

### Connection Refused Error

If you see `ConnectionRefusedError: [Errno 111] Connection refused`, ensure:

1. Docker daemon is running: `sudo systemctl status docker`
2. Services are up: `docker compose ps`
3. PostgreSQL is ready: `docker compose logs postgres`

### Database Connection Issues

```bash
# Check PostgreSQL container
docker compose exec postgres psql -U arl_user -d arl_dev

# Run migrations if tables are missing
.venv/bin/alembic upgrade head
```

### Port Already in Use

```bash
# Check what's using port 5432
lsof -i :5432

# Or port 6379 for Redis
lsof -i :6379

# Stop conflicting services or change ports in docker-compose.yml
```

## Development Workflow

1. Start Docker services: `docker compose up -d`
2. Run migrations if needed: `.venv/bin/alembic upgrade head`
3. Start backend: `.venv/bin/uvicorn app.main:app --reload`
4. Make changes - server auto-reloads
5. Stop when done: `docker compose down`
