# Quickstart Guide

Get started with ARL in 5 minutes.

## 1. Installation

### CLI Tool

```bash
# Install ARL with uv (recommended)
uv pip install -e .

# Or with standard pip
pip install -e .

# Set API key (choose one)
export GOOGLE_API_KEY="your-key"

# Initialize
arl init
```

### Backend & Frontend (Web UI)

**Terminal 1 - Backend:**
```bash
cd arl-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Or: .\venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with database, Redis settings

# Run migrations
alembic upgrade head

# Start Redis (required for WebSockets)
sudo systemctl start redis  # Linux
# Or: brew services start redis  # Mac

# Start backend server
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd arl-frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/docs

## 2. Run Complete Research Cycle

```bash
# Create project
arl project create --name "My Research" --domain cs

# Run research (replace <project-id> with ID from above)
arl research run \
  --project <project-id> \
  --request "Test if dropout improves neural network robustness" \
  --auto
```

**Result:** Complete research cycle in ~5-10 minutes
- Hypothesis generated
- Experiment designed
- Code generated & executed
- Results analyzed

## 3. View Results

```bash
# List sessions
arl research list --project <project-id>

# Check session details
arl research status --session <session-id>
```

## Common Workflows

### Algorithm Comparison

```bash
arl research run \
  --project <id> \
  --request "Compare Random Forest vs XGBoost on classification" \
  --auto
```

### Hypothesis Testing

```bash
arl research run \
  --project <id> \
  --request "Test: Batch normalization improves training stability by 30%" \
  --auto
```

### With Literature Review

```bash
# Ingest papers
arl paper ingest --project <id> --arxiv 2301.00001

# Generate hypotheses from papers
arl research run \
  --project <id> \
  --request "Generate testable hypotheses from ingested papers" \
  --auto
```

## Interactive Mode

Control each stage:

```bash
# Start research
arl research start \
  --project <id> \
  --request "Compare CNN vs Transformer architectures"

# Review hypotheses, then continue
arl research continue --session <session-id>

# Review experiment design & code, then continue
arl research continue --session <session-id>

# View final analysis
```

## Python API

```python
import asyncio
from arl.adk_agents.orchestrator.agent import create_orchestrator
from arl.core.project.project_service import ProjectService
from arl.core.session.session_service import SessionService
from arl.storage.database import init_db

# Setup
init_db()
project_service = ProjectService()
project = project_service.create_project("My Research", "cs")

session_service = SessionService()
session = session_service.create_session(project.project_id)

# Run research
async def run_research():
    orchestrator = create_orchestrator()

    class MockContext:
        pass

    result = await orchestrator.run(
        ctx=MockContext(),
        session_id=session.session_id,
        user_request="Your research question here"
    )

    return result

result = asyncio.run(run_research())
print(f"Stage: {result['stage']}")
```

## Docker Setup

Required for code execution:

```bash
# Start Docker
sudo systemctl start docker

# Build sandbox image
./scripts/build_sandbox.sh

# Verify
docker images arl-sandbox:latest
```

Without Docker:
- Hypotheses generated ✓
- Experiments designed ✓
- Code generated ✓
- Code execution ✗

## Configuration

```bash
# Choose LLM provider
export DEFAULT_LLM_PROVIDER=google  # or openai, anthropic

# Set timeout
export EXPERIMENT_TIMEOUT_SECONDS=600

# Enable/disable Docker
export DOCKER_ENABLED=true
```

## Example Output

```
Running complete research cycle...

✓ Session created: abc123
  Project: My Research

Stage: Hypothesis Generation
  ✓ Completed: hypothesis_generation

Stage: Experiment Design
  ✓ Completed: experiment_design

Stage: Execution & Analysis
  ✓ Completed: execution_complete

============================================================
RESEARCH CYCLE COMPLETE
============================================================

1. Hypothesis Generated
   Model: gemini-exp-1206
   Tokens: 3842

2. Experiment Designed & Code Generated
   Code length: 1523 chars
   Valid: True

3. Executed & Analyzed
   Execution success: True
   Analysis: Hypothesis SUPPORTED (confidence: 0.85)

Session ID: abc123
```

## Output Locations

- **Database:** `./data/arl.db`
- **Artifacts:** `./data/artifacts/<experiment-id>/`
  - Plots (PNG, PDF)
  - Data files (CSV, JSON)
- **Papers:** `./data/papers/<project-id>/`

## Command Reference

```bash
# Project management
arl project create --name "Name" --domain cs
arl project list
arl project show <id>

# Paper library
arl paper ingest --project <id> --arxiv <arxiv-id>
arl paper list --project <id>

# Research workflows
arl research start --project <id> --request "..."
arl research continue --session <id>
arl research run --project <id> --request "..." --auto
arl research status --session <id>
arl research list --project <id>

# System
arl init
arl --version
arl --help
```

## Troubleshooting

**API Key Not Found**
```bash
echo $GOOGLE_API_KEY  # Check if set
export GOOGLE_API_KEY="your-key"  # Set if missing
```

**Docker Not Running**
```bash
sudo systemctl start docker
docker ps  # Verify
```

**Module Not Found**
```bash
uv pip install -e .
python -c "import arl; print(arl.__version__)"
```

**Backend/Frontend Connection Issues**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check Redis is running
redis-cli ping  # Should return "PONG"

# Verify frontend env
cat arl-frontend/.env  # Should show VITE_API_URL
```

## Next Steps

1. **Full Documentation:** [docs/user-guide.md](user-guide.md)
2. **Examples:** [examples/README.md](../examples/README.md)
3. **Testing:** [docs/testing.md](testing.md)
4. **Architecture:** [docs/architecture.md](architecture.md)
