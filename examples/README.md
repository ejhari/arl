# ARL Usage Examples

Complete examples demonstrating the AI Autonomous Research Lab system.

## Contents

1. **`example_01_quick_start.py`** - Quick start with basic workflow
2. **`example_02_paper_ingestion.py`** - Paper library management
3. **`example_03_hypothesis_generation.py`** - Hypothesis generation agent
4. **`example_04_complete_workflow.py`** - Full research cycle
5. **`example_05_cli_workflow.sh`** - CLI-based research workflow

## Running Examples

### Prerequisites

```bash
# Install dependencies with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .

# Set API key (for LLM providers)
export GOOGLE_API_KEY="your-api-key"
# OR
export OPENAI_API_KEY="your-api-key"
# OR
export ANTHROPIC_API_KEY="your-api-key"

# Initialize ARL
arl init

# Start Docker (for code execution)
sudo systemctl start docker
./scripts/build_sandbox.sh
```

### Run Examples

```bash
# Python examples
python examples/example_01_quick_start.py
python examples/example_02_paper_ingestion.py
python examples/example_03_hypothesis_generation.py
python examples/example_04_complete_workflow.py

# CLI example
bash examples/example_05_cli_workflow.sh
```

## Example Descriptions

### Example 1: Quick Start

Demonstrates:
- Creating a project
- Starting a research session
- Running hypothesis generation
- Viewing results

**Use Case**: First-time users learning the system

### Example 2: Paper Ingestion

Demonstrates:
- Searching arXiv for papers
- Downloading and parsing PDFs
- Building a paper library
- Searching papers

**Use Case**: Literature review and knowledge base building

### Example 3: Hypothesis Generation

Demonstrates:
- Using the Hypothesis Agent
- Generating testable hypotheses
- Assessing novelty and feasibility
- Literature grounding

**Use Case**: Research ideation and hypothesis development

### Example 4: Complete Workflow

Demonstrates:
- Full research cycle (all 6 agents)
- Hypothesis → Experiment → Code → Execution → Analysis
- Session and memory management
- Result interpretation

**Use Case**: End-to-end autonomous research

### Example 5: CLI Workflow

Demonstrates:
- Using CLI commands for research
- Interactive vs automatic modes
- Monitoring progress
- Accessing results

**Use Case**: Command-line based research workflows

## Example Outputs

Each example includes:
- Clear console output with progress indicators
- Explanation of what's happening
- Sample results
- Next steps suggestions

## Advanced Examples

For advanced usage patterns, see:
- `RESEARCH_WORKFLOW_GUIDE.md` - Complete workflow documentation
- `TESTING.md` - Testing guide with examples
- Test suite in `tests/` - Programmatic examples
