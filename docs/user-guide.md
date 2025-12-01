# ARL User Guide

Complete guide to using the AI Autonomous Research Lab.

## Table of Contents

1. [Research Workflow](#research-workflow)
2. [Project Management](#project-management)
3. [Paper Library](#paper-library)
4. [Research Commands](#research-commands)
5. [Advanced Usage](#advanced-usage)
6. [Best Practices](#best-practices)

## Research Workflow

ARL automates the complete research pipeline:

```
User Request
    ↓
1. Hypothesis Generation
   → Generates 3-5 testable hypotheses
   → Ranks by feasibility/novelty/impact
    ↓
2. Experiment Design & Code Generation
   → Creates experimental protocol
   → Generates production-ready Python code
    ↓
3. Execution & Analysis
   → Runs code in Docker sandbox
   → Analyzes results statistically
   → Validates hypothesis
   → Recommends next steps
```

### Stage 1: Hypothesis Generation

```bash
arl research start \
  --project <project-id> \
  --request "Your research question"
```

**Input:**
- Research question or objective
- Optional: Literature context from papers

**Output:**
- 3-5 testable hypotheses
- Testability assessment
- Novelty score (0-1)
- Feasibility score (0-1)
- Literature grounding
- Expected impact

**Example:**
```
Hypothesis: "Adversarial training with PGD attacks improves model
            robustness by 25% compared to standard training."
Testability: High
Novelty: 0.6
Feasibility: 0.8
Literature: Goodfellow et al. (2015), Madry et al. (2018)
```

### Stage 2: Experiment Design & Code Generation

```bash
arl research continue --session <session-id>
```

**Input:**
- Selected hypothesis
- Domain & constraints

**Output:**
- Detailed experimental protocol
- Parameter specifications
- Statistical validation criteria
- Production-ready Python code
- Code validation results
- Dependency list

**Example:**
```
Experiment Design:
- Methods: Standard training vs Adversarial training
- Dataset: CIFAR-10
- Metrics: Clean accuracy, robust accuracy
- Statistical tests: Paired t-test, Cohen's d

Generated Code:
- 450 lines of validated Python
- Dependencies: numpy, torch, torchvision, matplotlib, scipy
```

### Stage 3: Execution & Analysis

```bash
arl research continue --session <session-id>
```

**Input:**
- Generated code
- Experiment ID

**Output:**
- Execution results (success/failure)
- Generated artifacts (plots, data files)
- Statistical analysis
- Hypothesis validation (SUPPORTED/REFUTED/INCONCLUSIVE)
- Confidence level
- Limitations
- Next step recommendations

**Example:**
```
Results:
- Success: True
- Runtime: 45 minutes
- Artifacts: 3 plots, 2 CSV files

Analysis:
- Hypothesis: SUPPORTED
- Confidence: 0.85
- Evidence: Robust accuracy improved 12% → 38% (p < 0.001)
- Limitations: Only tested on CIFAR-10
- Next Steps: Test on ImageNet, compare with other techniques
```

## Project Management

### Create Project

```bash
arl project create \
  --name "Project Name" \
  --domain cs \
  --objectives "Research objectives"
```

**Domains:**
- `cs` - Computer Science
- `biology` - Biological Sciences
- `physics` - Physical Sciences
- `general` - General Research

### List Projects

```bash
arl project list
```

### Show Project Details

```bash
arl project show <project-id>
```

**Output:**
- Project metadata
- Number of sessions
- Number of papers
- Creation date

## Paper Library

### Ingest Papers

**From arXiv:**
```bash
arl paper ingest --project <id> --arxiv 2301.00001
```

**Manual Upload:**
```bash
arl paper ingest --project <id> --file paper.pdf
```

### List Papers

```bash
arl paper list --project <id>
```

### Show Paper Details

```bash
arl paper show <paper-id>
```

### Search Papers

```bash
arl paper search --project <id> "query terms"
```

## Research Commands

### Start Research Session

```bash
arl research start \
  --project <project-id> \
  --request "Your research question"
```

Creates new session and executes Stage 1 (hypothesis generation).

### Continue Session

```bash
arl research continue --session <session-id>
```

Advances session to next stage.

### Run Complete Cycle

```bash
arl research run \
  --project <project-id> \
  --request "Your research question" \
  [--auto]
```

**Flags:**
- `--auto` - Run all stages automatically without pausing

**Interactive Mode (without --auto):**
- Pauses after each stage for review
- Requires manual continuation

**Automatic Mode (with --auto):**
- Runs all stages sequentially
- No manual intervention required

### Check Status

```bash
arl research status --session <session-id>
```

### List Sessions

```bash
arl research list --project <project-id>
```

## Advanced Usage

### Resume After Interruption

```bash
# Check current state
arl research status --session <session-id>

# Resume from where it stopped
arl research continue --session <session-id>
```

### Iterative Refinement

```bash
# First iteration
arl research run \
  --project <id> \
  --request "Broad research question" \
  --auto

# Analyze results, then refine
arl research run \
  --project <id> \
  --request "Refined hypothesis based on previous results" \
  --auto
```

### Custom Constraints

Include constraints in your request:

```bash
arl research run \
  --project <id> \
  --request "Test hypothesis X with constraints:
    - Maximum training time: 1 hour
    - Maximum GPU memory: 8GB
    - Must run on CPU-only machines" \
  --auto
```

### Python API Integration

```python
from arl.core.project.project_service import ProjectService
from arl.core.session.session_service import SessionService
from arl.storage.database import init_db

# Initialize
init_db()

# Create project
project_service = ProjectService()
project = project_service.create_project(
    name="API Research",
    domain="cs"
)

# Create session
session_service = SessionService()
session = session_service.create_session(project.project_id)

# Run research with orchestrator
from arl.adk_agents.orchestrator.agent import create_orchestrator
import asyncio

async def research():
    orchestrator = create_orchestrator()
    result = await orchestrator.run(
        ctx=MockContext(),
        session_id=session.session_id,
        user_request="Your research question"
    )
    return result

result = asyncio.run(research())
```

## Best Practices

### Writing Good Research Requests

**Good:**
```
"Test if dropout regularization reduces overfitting on small datasets
compared to early stopping"
```

**Better:**
```
"Compare three regularization techniques (dropout, L2, early stopping)
for preventing overfitting on CIFAR-10 with limited training data
(1k, 5k, 10k samples). Hypothesis: Dropout shows largest improvement
at 1k samples."
```

**Best:**
```
"Design controlled experiment to test hypothesis: Dropout regularization
(p=0.5) reduces overfitting by ≥20% compared to early stopping when
training ResNet-18 on CIFAR-10 with 1k samples. Measure via test
accuracy gap."
```

### Hypothesis Formulation

**Testable Hypothesis Elements:**
- Clear prediction
- Quantifiable outcome
- Baseline comparison
- Success criteria

**Example:**
```
"Algorithm A will outperform Algorithm B by at least X% on Metric M
when applied to Dataset D under Conditions C."
```

### Session Organization

**Single Focus:**
```bash
# Good: One hypothesis per session
arl research run --project <id> --request "Test hypothesis A" --auto
arl research run --project <id> --request "Test hypothesis B" --auto
```

**Avoid:**
```bash
# Bad: Multiple hypotheses in one request
arl research run --project <id> --request "Test A, B, and C" --auto
```

### Resource Management

**Monitor Long-Running Experiments:**
```bash
# Check progress
arl research status --session <session-id>

# Default timeout: 10 minutes
# Configure: export EXPERIMENT_TIMEOUT_SECONDS=3600
```

**Cleanup:**
```bash
# Archive completed sessions
arl session archive <session-id>

# Clean artifacts
rm -rf ./data/artifacts/<old-experiment-ids>
```

### Error Recovery

**Execution Failed:**
```bash
# Check error details
arl research status --session <session-id>

# Retry with modifications
arl research continue --session <session-id>
```

**Code Generation Issues:**
```bash
# Review generated code in session state
# Modify request and start new session
arl research start --project <id> --request "Modified request"
```

## Configuration

### Environment Variables

```bash
# LLM Provider
export GOOGLE_API_KEY="your-key"
export DEFAULT_LLM_PROVIDER=google

# Experiment settings
export EXPERIMENT_TIMEOUT_SECONDS=600
export MAX_CONCURRENT_EXPERIMENTS=3

# Docker
export DOCKER_ENABLED=true
```

### Model Selection

Edit `arl/config/settings.py`:

```python
# Fast models for simple tasks
CODE_GEN_MODEL = "gemini-2.0-flash-exp"

# Powerful models for complex reasoning
HYPOTHESIS_MODEL = "gemini-exp-1206"
ANALYSIS_MODEL = "gemini-exp-1206"
```

### Database Location

```bash
# Default: ./data/arl.db
export DATABASE_URL="sqlite:///./data/arl.db"

# Custom location
export DATABASE_URL="sqlite:////home/user/research/arl.db"
```

## Output Locations

```
arl/
├── data/
│   ├── arl.db                    # Project/session metadata
│   ├── papers/
│   │   └── <project-id>/
│   │       └── *.pdf             # Ingested papers
│   └── artifacts/
│       └── <experiment-id>/
│           ├── *.png             # Generated plots
│           ├── *.csv             # Data files
│           └── *.json            # Results
```

## Troubleshooting

See [docs/troubleshooting.md](troubleshooting.md) for detailed troubleshooting guide.

## Next Steps

- [Examples](../examples/README.md) - Sample workflows
- [Testing Guide](testing.md) - Run test suite
- [Architecture](architecture.md) - System design
- [API Reference](api-reference.md) - Python API docs
