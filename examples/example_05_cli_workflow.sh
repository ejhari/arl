#!/bin/bash
#
# Example 5: CLI-Based Research Workflow
#
# This example demonstrates using ARL entirely through CLI commands.
# It shows both interactive and automatic modes.
#
# Run: bash examples/example_05_cli_workflow.sh

set -e  # Exit on error

echo "=================================="
echo "ARL CLI Workflow Example"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
ARL_BIN="$PROJECT_ROOT/.venv/bin/arl"

# Check if arl command exists
if [ ! -f "$ARL_BIN" ]; then
    echo -e "${YELLOW}Error: ARL CLI not found at $ARL_BIN${NC}"
    echo "Please run: uv pip install -e . from the project root"
    exit 1
fi

echo "Using ARL CLI: $ARL_BIN"
echo ""

# Step 1: Initialize ARL
echo -e "${CYAN}Step 1: Initialize ARL${NC}"
$ARL_BIN init
echo ""

# Step 2: Create a project
echo -e "${CYAN}Step 2: Create Research Project${NC}"
$ARL_BIN project create \
  --name "CLI Example Project" \
  --domain cs \
  --objectives "Demonstrate CLI-based research workflow"

echo ""
echo -e "${YELLOW}Note: Copy the project ID from above for next steps${NC}"
echo "Enter project ID:"
read PROJECT_ID
echo ""

# Step 3: List projects to verify
echo -e "${CYAN}Step 3: List Projects${NC}"
$ARL_BIN project list
echo ""

# Step 4: Show project details
echo -e "${CYAN}Step 4: Show Project Details${NC}"
$ARL_BIN project show $PROJECT_ID
echo ""

# Step 5: Start research session (interactive mode)
echo -e "${CYAN}Step 5: Start Research Session (Interactive)${NC}"
echo "This will generate hypotheses..."
echo ""

$ARL_BIN research start \
  --project $PROJECT_ID \
  --request "Compare deep learning architectures for image classification: CNNs vs Vision Transformers"

echo ""
echo -e "${YELLOW}Note: Copy the session ID from above${NC}"
echo "Enter session ID:"
read SESSION_ID
echo ""

# Step 6: Check session status
echo -e "${CYAN}Step 6: Check Session Status${NC}"
$ARL_BIN research status --session $SESSION_ID
echo ""

# Step 7: Continue to next stage
echo -e "${CYAN}Step 7: Continue to Experiment Design${NC}"
echo "Press Enter to continue to experiment design stage..."
read

$ARL_BIN research continue --session $SESSION_ID
echo ""

# Step 8: Continue to execution
echo -e "${CYAN}Step 8: Continue to Execution & Analysis${NC}"
echo "Press Enter to continue to execution stage..."
echo -e "${YELLOW}Note: This requires Docker to be running${NC}"
read

# This would execute, but we'll skip in example
echo -e "${YELLOW}Skipping execution stage (requires Docker)${NC}"
echo ""

# Step 9: List all sessions
echo -e "${CYAN}Step 9: List All Sessions${NC}"
$ARL_BIN research list --project $PROJECT_ID
echo ""

# Step 10: Demonstrate automatic mode
echo -e "${CYAN}Step 10: Run Complete Workflow (Automatic Mode)${NC}"
echo "This runs all stages automatically without pausing"
echo "Press Enter to start automatic research workflow..."
read

$ARL_BIN research run \
  --project $PROJECT_ID \
  --request "Test hypothesis: ResNet-50 achieves higher accuracy than VGG-16 on CIFAR-10" \
  --auto

echo ""
echo -e "${GREEN}=================================="
echo "CLI Workflow Example Complete!"
echo "==================================${NC}"
echo ""

# Summary
echo "Summary of what we did:"
echo "1. Initialized ARL database"
echo "2. Created a research project"
echo "3. Started an interactive research session"
echo "4. Generated hypotheses (Stage 1)"
echo "5. Designed experiment (Stage 2)"
echo "6. (Skipped execution - requires Docker)"
echo "7. Ran complete automatic workflow"
echo ""

echo "Useful Commands:"
echo "  - View all projects: $ARL_BIN project list"
echo "  - View project details: $ARL_BIN project show <project-id>"
echo "  - View session status: $ARL_BIN research status --session <session-id>"
echo "  - List sessions: $ARL_BIN research list --project <project-id>"
echo "  - Continue session: $ARL_BIN research continue --session <session-id>"
echo "  - Run complete cycle: $ARL_BIN research run --project <id> --request '...' --auto"
echo ""
echo "See RESEARCH_WORKFLOW_GUIDE.md for complete documentation"
echo ""
