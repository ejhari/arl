# ARL Research Workflow Guide

Complete guide to running autonomous research cycles with ARL.

## Quick Start

### 1. Initialize ARL

```bash
arl init
```

### 2. Create a Project

```bash
arl project create --name "ML Research" --domain cs --objectives "Study neural network robustness"
```

### 3. Run Complete Research Cycle

```bash
# Get your project ID from the project list
arl project list

# Run a complete research cycle (all stages automatically)
arl research run \
  --project <project-id> \
  --request "Test hypothesis: Data augmentation improves model robustness on out-of-distribution samples" \
  --auto
```

## Research Workflow Commands

### `arl research start`

Start a new research session and execute the first stage (hypothesis generation).

**Usage:**
```bash
arl research start \
  --project <project-id> \
  --request "Your research question or hypothesis"
```

**Example:**
```bash
arl research start \
  --project abc123 \
  --request "Compare convolutional vs transformer architectures for image classification"
```

**Output:**
- Creates new session
- Generates testable hypotheses
- Displays session ID for continuing

### `arl research continue`

Continue an existing research session to the next stage.

**Usage:**
```bash
arl research continue --session <session-id>
```

**Example:**
```bash
arl research continue --session def456
```

**Workflow Stages:**
1. **Hypothesis Generation** → Generates testable research hypotheses
2. **Experiment Design** → Creates experimental protocol and Python code
3. **Execution & Analysis** → Runs experiment and analyzes results

### `arl research run`

Run a complete research cycle from start to finish.

**Usage:**
```bash
arl research run \
  --project <project-id> \
  --request "Your research question" \
  [--auto]
```

**Flags:**
- `--auto`: Run all stages automatically without pausing for confirmation

**Example (Interactive):**
```bash
arl research run \
  --project abc123 \
  --request "Evaluate the effectiveness of dropout regularization"
```

**Example (Automatic):**
```bash
arl research run \
  --project abc123 \
  --request "Test if batch normalization improves training stability" \
  --auto
```

**Complete Workflow:**
```
User Request
    ↓
1. Hypothesis Generation
   - Generates 3-5 testable hypotheses
   - Assesses novelty and feasibility
   - Grounds in literature
    ↓
2. Experiment Design & Code Generation
   - Creates experimental protocol
   - Generates production-ready Python code
   - Validates code safety
    ↓
3. Execution & Analysis
   - Runs code in Docker sandbox
   - Collects results and artifacts
   - Analyzes results statistically
   - Validates hypothesis (SUPPORTED/REFUTED/INCONCLUSIVE)
   - Recommends next steps
```

### `arl research status`

Show current status of a research session.

**Usage:**
```bash
arl research status --session <session-id>
```

**Example:**
```bash
arl research status --session def456
```

**Output:**
- Session metadata (ID, project, status)
- Current workflow stage
- Available data and checkpoints
- Event log summary

### `arl research list`

List all research sessions for a project.

**Usage:**
```bash
arl research list --project <project-id>
```

**Example:**
```bash
arl research list --project abc123
```

**Output:**
- All sessions with status
- Creation and update timestamps
- Current workflow stage

## Complete Example Workflow

### Example: Neural Network Robustness Study

**Step 1: Setup**
```bash
# Initialize ARL
arl init

# Create project
arl project create \
  --name "Robustness Study" \
  --domain cs \
  --objectives "Investigate neural network robustness techniques"

# Note the project ID (e.g., a1b2c3d4-...)
```

**Step 2: Ingest Literature**
```bash
# Add relevant papers to the project
arl paper ingest --project a1b2c3d4 --arxiv 2301.00001
arl paper ingest --project a1b2c3d4 --arxiv 2302.00002

# List papers
arl paper list --project a1b2c3d4
```

**Step 3: Run Research Cycle (Interactive)**
```bash
# Start research session
arl research start \
  --project a1b2c3d4 \
  --request "Generate hypotheses about improving neural network robustness to adversarial examples"

# Output shows generated hypotheses and session ID (e.g., e5f6g7h8-...)

# Continue to experiment design
arl research continue --session e5f6g7h8

# Output shows experimental protocol and generated code

# Continue to execution
arl research continue --session e5f6g7h8

# Output shows execution results and analysis
```

**Step 4: Run Research Cycle (Automatic)**
```bash
# Run complete cycle without pausing
arl research run \
  --project a1b2c3d4 \
  --request "Test hypothesis: Adversarial training improves robustness to FGSM attacks" \
  --auto

# Output shows all three stages completed with final analysis
```

## Workflow Stages Explained

### Stage 1: Hypothesis Generation

**Agent:** Hypothesis Agent
**Input:** Literature summary, research gap, domain
**Output:**
- 3-5 testable hypotheses
- Testability assessment
- Novelty score (0-1)
- Feasibility score (0-1)
- Literature grounding
- Expected impact

**Example Output:**
```
Hypothesis 1: "Adversarial training with PGD attacks improves model robustness
              by 25% compared to standard training."
Testability: High - Can be validated through controlled experiments
Novelty: 0.6 - Builds on existing adversarial training literature
Feasibility: 0.8 - Requires GPU compute but achievable
Literature: Goodfellow et al. (2015), Madry et al. (2018)
```

### Stage 2: Experiment Design & Code Generation

**Agents:** Experiment Designer Agent + Code Generator Agent
**Input:** Selected hypothesis, domain, constraints
**Output:**
- Detailed experimental protocol
- Parameter specifications
- Statistical validation criteria
- Production-ready Python code
- Code validation results
- Dependency list

**Example Output:**
```
Experiment Design:
- Template: ML Comparison
- Methods: Standard training vs Adversarial training (PGD)
- Dataset: CIFAR-10
- Metrics: Clean accuracy, robust accuracy (FGSM, PGD)
- Statistical tests: Paired t-test, effect size (Cohen's d)
- Baseline: Standard SGD training

Generated Code:
- 450 lines of validated Python
- Includes: data loading, model training, adversarial attack generation,
           evaluation, statistical testing, visualization
- Dependencies: numpy, torch, torchvision, matplotlib, scipy
```

### Stage 3: Execution & Analysis

**Agents:** Execution Engine Agent + Analysis Agent
**Input:** Generated code, experiment ID
**Output:**
- Execution results (success/failure)
- Standard output and errors
- Generated artifacts (plots, data files)
- Statistical analysis
- Hypothesis validation outcome
- Confidence level
- Limitations identified
- Next step recommendations

**Example Output:**
```
Execution Results:
- Success: True
- Runtime: 45 minutes
- Artifacts: 3 plots, 2 CSV files

Analysis:
- Hypothesis: SUPPORTED
- Confidence: 0.85
- Evidence: Adversarial training improved robust accuracy from 12% to 38%
            (p < 0.001, Cohen's d = 2.3)
- Limitations: Only tested on CIFAR-10, single architecture (ResNet-18)
- Next Steps:
  1. Test on ImageNet with larger models
  2. Compare with other robustness techniques (certified defenses)
  3. Analyze computational cost trade-offs
```

## Advanced Usage

### Resume After Interruption

```bash
# If workflow is interrupted, resume with continue
arl research status --session <session-id>  # Check current state
arl research continue --session <session-id>
```

### Run Multiple Iterations

```bash
# Run first iteration
arl research run --project <id> --request "Hypothesis 1" --auto

# Analyze results and refine
arl research run --project <id> --request "Refined hypothesis based on previous results" --auto
```

### Monitor Progress

```bash
# Check session status during long-running experiments
arl research status --session <session-id>

# List all sessions to track multiple research threads
arl research list --project <project-id>
```

## Integration with Other Commands

### Complete Research Workflow

```bash
# 1. Create project
PROJECT_ID=$(arl project create --name "Study" --domain cs | grep "Project created" | awk '{print $4}')

# 2. Ingest papers
arl paper ingest --project $PROJECT_ID --arxiv 2301.00001

# 3. Run research
arl research run \
  --project $PROJECT_ID \
  --request "Generate and test hypotheses from ingested papers" \
  --auto

# 4. View results
arl research list --project $PROJECT_ID
```

## Tips and Best Practices

### Writing Good Research Requests

**Good:**
```
"Test the hypothesis that dropout regularization reduces overfitting
 on small datasets (< 10k samples) compared to early stopping"
```

**Better:**
```
"Compare three regularization techniques (dropout, L2, early stopping)
 for preventing overfitting on CIFAR-10 with limited training data (1k, 5k, 10k samples).
 Hypothesis: Dropout will show the largest improvement at 1k samples."
```

### Constraints

You can specify constraints in your request:
```
"Design an experiment to test X with constraints:
 - Maximum training time: 1 hour
 - Maximum GPU memory: 8GB
 - Must run on CPU-only machines"
```

### Iterative Refinement

```bash
# First iteration - broad exploration
arl research run --project $ID --request "Compare ML algorithms" --auto

# Second iteration - focused based on results
arl research run --project $ID --request "Deep dive into best performing algorithm from previous experiment" --auto
```

## Troubleshooting

### Session Not Found

```bash
# List all sessions to find the correct ID
arl research list --project <project-id>
```

### Experiment Execution Failed

```bash
# Check session status for error details
arl research status --session <session-id>

# Review generated code (stored in session state)
# Re-run with continue to retry
arl research continue --session <session-id>
```

### Long Running Experiments

The execution stage can take time depending on the experiment. The system will:
- Show progress spinner
- Execute in isolated Docker container
- Timeout after configured limit (default: 10 minutes)
- Collect all artifacts even if timeout occurs

## Output Locations

- **Session Data**: SQLite database (`./data/arl.db`)
- **Experiment Artifacts**: `./data/artifacts/<experiment-id>/`
  - Generated plots (PNG, PDF)
  - Data files (CSV, JSON)
  - Model checkpoints
- **PDFs**: `./data/papers/<project-id>/`

## Next Steps

After completing a research cycle:

1. **Review Analysis**: Check hypothesis validation and confidence
2. **Examine Artifacts**: View generated plots and data
3. **Iterate**: Use recommendations to design next experiment
4. **Document**: Export results for publication
5. **Share**: Session IDs can be shared for reproducibility

## Complete Command Reference

```bash
# Project Management
arl project create --name "Name" --domain cs
arl project list
arl project show <project-id>

# Paper Library
arl paper ingest --project <id> --arxiv <arxiv-id>
arl paper list --project <id>
arl paper show <paper-id>

# Research Workflows
arl research start --project <id> --request "..."
arl research continue --session <id>
arl research run --project <id> --request "..." [--auto]
arl research status --session <id>
arl research list --project <id>

# System
arl init
arl --version
arl --help
```
