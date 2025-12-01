# AI Autonomous Research Lab (ARL)

Multi-agent scientific research automation system built on Google's Agent Development Kit (ADK).

## Overview

ARL automates the complete scientific research pipeline:
- Literature review and paper ingestion
- Hypothesis generation from research gaps
- Experiment design and validation
- Python code generation for experiments
- Sandboxed execution with result capture
- Statistical analysis and hypothesis validation
- Research report generation

## Quick Start

### CLI Tool

```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install ARL
uv pip install -e .

# Set API key
export GOOGLE_API_KEY="your-key"

# Initialize
arl init

# Create project
arl project create --name "My Research" --domain cs

# Run research
arl research run --project <id> --request "Test hypothesis" --auto
```

### Web UI (Backend + Frontend)

**Terminal 1 - Backend:**
```bash
cd arl-backend
python -m venv venv && source venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env  # Configure settings
alembic upgrade head
sudo systemctl start redis  # Or: brew services start redis
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd arl-frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

Access at http://localhost:5173

## Features

- **Multi-domain support**: Computer Science, Biology, Physics, General Research
- **Provider-agnostic LLM**: Google Gemini, OpenAI, Anthropic, Azure OpenAI
- **Hybrid deployment**: Run locally or on Google Cloud
- **A2A Protocol**: Standardized agent-to-agent communication for microservices architecture
- **Interactive collaboration**: Human-in-the-loop at any stage
- **Reproducible research**: Complete experiment versioning and artifact management
- **Docker sandbox**: Secure isolated execution environment

## Documentation

### Getting Started
- [Installation Guide](docs/installation.md) - Setup and prerequisites
- [Quickstart Guide](docs/quickstart.md) - Get running in 5 minutes
- [User Guide](docs/user-guide.md) - Complete feature documentation

### Architecture & Deployment
- [Architecture Overview](docs/architecture.md) - System design and components
- [A2A Protocol Guide](docs/a2a-protocol.md) - Agent-to-agent communication and microservices

### Provider Setup
- [Azure OpenAI Setup](docs/azure-setup.md) - Configure Azure OpenAI

### Examples & References
- [Examples Directory](examples/README.md) - Sample workflows and code
- [Research Workflow Guide](docs/research-workflow-guide.md) - Detailed workflow documentation

## Architecture

Built on Google ADK with specialized agents:
- **Orchestrator**: Main workflow coordination
- **Literature Agent**: Paper ingestion and analysis
- **Hypothesis Agent**: Testable hypothesis generation
- **Experiment Designer**: Protocol and parameter specification
- **Code Generator**: Python code generation with validation
- **Execution Engine**: Docker sandbox execution
- **Analysis Agent**: Statistical validation and interpretation

See [Architecture Overview](docs/architecture.md) for detailed system design.

## Project Structure

```
arl/
├── docs/                      # Documentation
│   ├── installation.md
│   ├── quickstart.md
│   ├── user-guide.md
│   ├── architecture.md
│   ├── testing.md
│   ├── azure-setup.md
│   └── frontend-development.md
├── arl/                       # Main package
│   ├── adk_agents/            # ADK agent implementations
│   ├── core/                  # Core business logic
│   ├── integrations/          # External integrations
│   ├── cli/                   # Command-line interface
│   └── storage/               # Data persistence
├── arl-frontend/              # React web UI
├── tests/                     # Test suite
├── examples/                  # Example workflows
└── scripts/                   # Utility scripts
```

## Technology Stack

- **Framework**: Google ADK 1.0+, Python 3.10+
- **LLM**: LiteLLM (Google Gemini, OpenAI, Anthropic, Azure OpenAI)
- **Execution**: Docker (sandboxed experiments)
- **Storage**: SQLite (local), Cloud SQL (cloud)
- **Scientific Stack**: NumPy, pandas, scikit-learn, PyTorch
- **Frontend**: React 18, TypeScript, Tailwind CSS, shadcn/ui

## Contributing

We welcome contributions! Please see our development guides:
- [Testing Guide](docs/testing.md)
- [Frontend Development](docs/frontend-development.md)

## License

MIT License - See LICENSE file

## Citation

If you use ARL in your research, please cite:

```bibtex
@software{arl2025,
  title={AI Autonomous Research Lab},
  author={ARL Team},
  year={2025},
  url={https://github.com/your-org/arl}
}
```
