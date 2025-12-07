# Installation Guide

## Prerequisites

- Python 3.10 or higher
- Docker (for code execution)
- Git
- API key for at least one LLM provider (Google/OpenAI/Anthropic)
- **uv** (recommended) - Fast Python package installer: https://github.com/astral-sh/uv

## Quick Install

### Install uv (Recommended)

```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Install ARL

```bash
# Clone or navigate to ARL directory
cd /path/to/arl

# Install package with uv (recommended - much faster)
uv pip install -e .

# Or with development dependencies
uv pip install -e ".[dev]"

# Or use standard pip
pip install -e .

# Initialize ARL
arl init
```

## Backend & Frontend Setup

### Backend (FastAPI + WebSockets)

```bash
cd arl-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Or: .\venv\Scripts\activate  # Windows

# Install dependencies with uv
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (database, Redis, etc.)

# Run database migrations
alembic upgrade head
```

### Frontend (React + TypeScript + Vite)

```bash
cd arl-frontend

# Install Node.js dependencies
npm install

# Configure environment
cp .env.example .env
```

### Redis Setup (Required for Backend)

**Linux:**
```bash
# Install Redis
sudo apt install redis-server  # Debian/Ubuntu
sudo dnf install redis  # Fedora

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis  # Start on boot

# Verify
redis-cli ping  # Should return "PONG"
```

**macOS:**
```bash
# Install with Homebrew
brew install redis

# Start Redis
brew services start redis

# Verify
redis-cli ping
```

**Windows (WSL2):**
```bash
# In WSL2
sudo apt install redis-server
sudo service redis-server start
redis-cli ping
```

## LLM Provider Setup

Choose and configure at least one provider:

### Google Gemini (Recommended)

```bash
# Get API key from: https://aistudio.google.com/app/apikey
export GOOGLE_API_KEY="your-google-api-key"

# Or add to .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

### Azure OpenAI

See [docs/azure-setup.md](azure-setup.md) for detailed Azure OpenAI configuration.

### OpenAI

```bash
export OPENAI_API_KEY="your-openai-api-key"
# Or in .env
echo "OPENAI_API_KEY=your-key" >> .env
```

### Anthropic Claude

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
# Or in .env
echo "ANTHROPIC_API_KEY=your-key" >> .env
```

## Docker Setup

Required for executing generated experiment code.

### Linux

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Start Docker
sudo systemctl start docker

# Add user to docker group (optional, avoids sudo)
sudo usermod -aG docker $USER
newgrp docker

# Build ARL sandbox image
./scripts/build_sandbox.sh
```

### macOS

```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version

# Build ARL sandbox image
./scripts/build_sandbox.sh
```

### Windows (WSL2)

```bash
# Install Docker Desktop with WSL2 backend
# Follow: https://docs.docker.com/desktop/windows/install/

# In WSL2 terminal
cd /path/to/arl
./scripts/build_sandbox.sh
```

## Verify Installation

### CLI Tool
```bash
# Check ARL version
arl --version

# Check installation
python -c "import arl; print(f'ARL {arl.__version__} installed')"

# Verify Docker sandbox
docker images arl-sandbox:latest

# Create test project
arl project create --name "Test" --domain cs
arl project list
```

### Backend & Frontend
```bash
# Verify backend (in separate terminal)
cd arl-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Test backend health endpoint
curl http://localhost:8000/health

# Verify frontend (in separate terminal)
cd arl-frontend
npm run dev

# Access frontend at http://localhost:5173
# Access API docs at http://localhost:8000/api/v1/docs
```

## Configuration

### Environment Variables

Configure environment in each component directory:

**Backend (`arl-backend/.env`):**
```bash
cp .env.example .env
# Edit with your database, Redis, and LLM API keys
```

**Frontend (`arl-frontend/.env`):**
```bash
cp .env.example .env
# Edit VITE_API_URL if backend runs on different port
```

### Settings File

Edit `arl/config/settings.py` for advanced configuration:

```python
# Model selection per agent
HYPOTHESIS_MODEL = "gemini-exp-1206"
CODE_GEN_MODEL = "gemini-2.0-flash-exp"
ANALYSIS_MODEL = "gemini-exp-1206"

# Resource limits
MAX_MEMORY_MB = 2048
MAX_CPU_PERCENT = 80
```

## Optional Components

### Jupyter Support

```bash
uv pip install jupyter notebook
```

### Cloud Deployment

See [docs/cloud-deployment.md](cloud-deployment.md) for GCP setup.

## Troubleshooting

### Module Not Found

```bash
# Reinstall package with uv
uv pip install -e .

# Or with pip
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Docker Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo (not recommended)
sudo arl research run ...
```

### API Key Not Found

```bash
# Check environment variable
echo $GOOGLE_API_KEY

# Set if missing
export GOOGLE_API_KEY="your-key"

# Or add to ~/.bashrc / ~/.zshrc
echo 'export GOOGLE_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Database Locked

```bash
# Close other ARL processes
pkill -f arl

# Reset database (WARNING: deletes data)
rm data/arl.db
arl init
```

## Next Steps

- [Quickstart Guide](quickstart.md) - Run your first research cycle
- [User Guide](user-guide.md) - Complete feature documentation
- [Examples](../examples/README.md) - Sample workflows
