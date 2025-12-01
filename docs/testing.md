# Testing Guide

## Prerequisites

- Python 3.10+
- Docker installed and running
- ARL dependencies installed

## Quick Test

```bash
# Install with dev dependencies using uv (recommended)
uv pip install -e ".[dev]"

# Or with standard pip
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=arl --cov-report=html
```

## Setup

### 1. Install Dependencies

```bash
# With uv (recommended)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### 2. Start Docker

```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application

# Verify
docker ps
```

### 3. Build Sandbox Image

```bash
chmod +x scripts/build_sandbox.sh
./scripts/build_sandbox.sh
```

**Expected output:**
```
Building ARL sandbox Docker image...
✓ Sandbox image built successfully
✓ Sandbox image verified
```

## Test Suites

### Unit Tests

```bash
# All unit tests
pytest tests/unit/ -v

# Specific component
pytest tests/unit/test_project_service.py -v
pytest tests/unit/test_session_service.py -v
```

### Integration Tests

```bash
# All integration tests
pytest tests/integration/ -v

# Specific workflow
pytest tests/integration/test_research_workflow.py -v
```

### Sandbox Tests

```bash
# Manual sandbox test
python scripts/test_sandbox.py
```

**Expected output:**
```
============================================================
ARL Sandbox Executor Test Suite
============================================================

Testing basic Python execution...
✓ Basic execution test passed

Testing scientific libraries...
✓ Scientific libraries test passed

Testing artifact generation...
✓ Artifact generation test passed

Testing error handling...
✓ Error handling test passed

============================================================
✓ All tests passed!
============================================================
```

## CLI Tests

### Initialize Database

```bash
arl init
```

### Create Test Project

```bash
arl project create --name "Test" --domain cs
arl project list
```

### Test Research Workflow

```bash
# Get project ID from list command
PROJECT_ID="<your-project-id>"

# Run quick research test
arl research run \
  --project $PROJECT_ID \
  --request "Test: Compare two sorting algorithms" \
  --auto
```

## Manual Docker Tests

### Test 1: Basic Execution

```bash
docker run --rm arl-sandbox:latest python -c "print('Hello from sandbox')"
```

### Test 2: Scientific Libraries

```bash
docker run --rm arl-sandbox:latest python -c "
import numpy as np
import pandas as pd
print(f'NumPy: {np.__version__}')
print(f'Pandas: {pd.__version__}')
print(f'Mean: {np.array([1,2,3]).mean()}')
"
```

### Test 3: Volume Mounting

```bash
# Create test directory
mkdir -p /tmp/sandbox_test
echo "print('Test from mounted file')" > /tmp/sandbox_test/test.py

# Run with volume
docker run --rm \
    -v /tmp/sandbox_test:/workspace \
    arl-sandbox:latest \
    python /workspace/test.py

# Cleanup
rm -rf /tmp/sandbox_test
```

## Database Tests

```python
# Test database models
python -c "
from arl.storage.database import init_db
from arl.storage.models import Project, Session, Paper, Experiment

init_db()
print('✓ Database initialized')
print('✓ Models loaded successfully')
"
```

## Example Workflows

### Example 1: Quick Start

```bash
python examples/example_01_quick_start.py
```

### Example 2: Paper Ingestion

```bash
python examples/example_02_paper_ingestion.py
```

### Example 3: Complete Workflow

```bash
python examples/example_04_complete_workflow.py
```

### Example 4: CLI Workflow

```bash
bash examples/example_05_cli_workflow.sh
```

## Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=arl --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Continuous Integration

### Run All Checks

```bash
# Linting
ruff check arl/

# Type checking
mypy arl/

# Tests
pytest tests/ -v

# Coverage
pytest tests/ --cov=arl --cov-report=term-missing
```

## Troubleshooting

### Docker Not Running

```bash
# Check status
systemctl status docker  # Linux
docker ps  # All platforms

# Start Docker
sudo systemctl start docker  # Linux
# Or start Docker Desktop application
```

### Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo (not recommended)
sudo pytest tests/
```

### Image Not Found

```bash
# List Docker images
docker images

# Rebuild if missing
./scripts/build_sandbox.sh
```

### Import Errors

```bash
# Reinstall package with uv
uv pip install -e .

# Or with pip
pip install -e .

# Check installation
python -c "import arl; print(arl.__version__)"

# Check Python path
python -c "import sys; print(sys.path)"
```

### Test Failures

```bash
# Run specific test with verbose output
pytest tests/test_name.py -v -s

# Show print statements
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x
```

### Database Locked

```bash
# Close other ARL processes
pkill -f arl

# Reset database
rm data/arl.db
arl init
```

## Test Structure

```
tests/
├── unit/                       # Unit tests
│   ├── test_project_service.py
│   ├── test_session_service.py
│   ├── test_paper_service.py
│   └── test_experiment.py
├── integration/                # Integration tests
│   ├── test_research_workflow.py
│   ├── test_paper_ingestion.py
│   └── test_sandbox_execution.py
└── conftest.py                 # Pytest configuration
```

## Next Steps

- Run tests before committing code
- Add new tests for new features
- Maintain > 80% code coverage
- Review test failures in CI/CD
