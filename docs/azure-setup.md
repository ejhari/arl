# Azure OpenAI Setup Guide

Complete guide for using Azure OpenAI with ARL.

## Prerequisites

- Azure subscription
- Azure OpenAI Service access (requires application approval)
- Azure CLI installed (optional)

## Azure OpenAI Service Setup

### 1. Create Azure OpenAI Resource

**Via Azure Portal:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Create new resource → AI + Machine Learning → Azure OpenAI
3. Fill in details:
   - Subscription
   - Resource group (create new or use existing)
   - Region (choose nearest available)
   - Name (unique identifier)
   - Pricing tier (Standard S0)
4. Review + Create

**Via Azure CLI:**

```bash
# Login
az login

# Create resource group (if needed)
az group create --name arl-rg --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name arl-openai \
  --resource-group arl-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

### 2. Deploy Models

**Via Azure Portal:**

1. Go to your Azure OpenAI resource
2. Navigate to "Model deployments" → "Manage Deployments"
3. Deploy models:
   - `gpt-4` (for complex reasoning)
   - `gpt-4-turbo` (for faster responses)
   - `gpt-35-turbo` (for simple tasks)

**Via Azure CLI:**

```bash
# Deploy GPT-4
az cognitiveservices account deployment create \
  --name arl-openai \
  --resource-group arl-rg \
  --deployment-name gpt-4-deployment \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --scale-settings-scale-type "Standard"
```

### 3. Get Credentials

**Endpoint:**
```bash
# Via Azure Portal
Resource → Keys and Endpoint → Copy Endpoint

# Via Azure CLI
az cognitiveservices account show \
  --name arl-openai \
  --resource-group arl-rg \
  --query properties.endpoint
```

**API Key:**
```bash
# Via Azure Portal
Resource → Keys and Endpoint → Copy Key 1

# Via Azure CLI
az cognitiveservices account keys list \
  --name arl-openai \
  --resource-group arl-rg \
  --query key1
```

## ARL Configuration

### Option 1: Environment Variables

```bash
# Set Azure OpenAI credentials
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"

# Set deployment names
export AZURE_OPENAI_DEPLOYMENT_GPT4="gpt-4-deployment"
export AZURE_OPENAI_DEPLOYMENT_GPT35="gpt-35-turbo-deployment"

# Set as default provider
export DEFAULT_LLM_PROVIDER="azure"
```

### Option 2: .env File

Create `.env` file in project root:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Deployment names (must match your Azure deployments)
AZURE_OPENAI_DEPLOYMENT_GPT4=gpt-4-deployment
AZURE_OPENAI_DEPLOYMENT_GPT35=gpt-35-turbo-deployment
AZURE_OPENAI_DEPLOYMENT_GPT4_TURBO=gpt-4-turbo-deployment

# Set as default
DEFAULT_LLM_PROVIDER=azure
```

### Option 3: Settings File

Edit `arl/config/settings.py`:

```python
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = "your-api-key"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"

# Model deployments
AZURE_OPENAI_DEPLOYMENT_GPT4 = "gpt-4-deployment"
AZURE_OPENAI_DEPLOYMENT_GPT35 = "gpt-35-turbo-deployment"

# Agent-specific models
HYPOTHESIS_MODEL = "azure/gpt-4-deployment"
CODE_GEN_MODEL = "azure/gpt-35-turbo-deployment"
ANALYSIS_MODEL = "azure/gpt-4-deployment"
```

## Model Selection

### Deployment Naming Convention

Map OpenAI models to Azure deployments:

```python
# In settings.py or .env
MODEL_MAPPING = {
    "gpt-4": "azure/gpt-4-deployment",
    "gpt-4-turbo": "azure/gpt-4-turbo-deployment",
    "gpt-3.5-turbo": "azure/gpt-35-turbo-deployment"
}
```

### Agent Configuration

```python
# Powerful model for complex reasoning
HYPOTHESIS_MODEL = "azure/gpt-4-deployment"
ANALYSIS_MODEL = "azure/gpt-4-deployment"

# Fast model for simple tasks
CODE_GEN_MODEL = "azure/gpt-35-turbo-deployment"
PAPER_PARSING_MODEL = "azure/gpt-35-turbo-deployment"
```

## Usage

### CLI Commands

```bash
# Verify configuration
arl --version
echo $AZURE_OPENAI_ENDPOINT

# Create project
arl project create --name "Azure Test" --domain cs

# Run research with Azure OpenAI
arl research run \
  --project <project-id> \
  --request "Test hypothesis" \
  --auto
```

### Python API

```python
from arl.integrations.llm.provider import get_llm_client

# Get Azure OpenAI client
client = get_llm_client(provider="azure")

# Use in research workflow
from arl.adk_agents.orchestrator.agent import create_orchestrator

orchestrator = create_orchestrator(
    llm_provider="azure"
)

result = await orchestrator.run(
    ctx=MockContext(),
    session_id=session_id,
    user_request="Your research question"
)
```

## Cost Management

### Deployment Configuration

```bash
# Standard deployment (pay-per-use)
az cognitiveservices account deployment create \
  --scale-settings-scale-type "Standard"

# Provisioned deployment (reserved capacity)
az cognitiveservices account deployment create \
  --scale-settings-scale-type "Provisioned" \
  --scale-settings-capacity 100
```

### Usage Monitoring

**Via Azure Portal:**
1. Go to your Azure OpenAI resource
2. Navigate to "Metrics"
3. View:
   - Total Calls
   - Total Tokens
   - Estimated Cost

**Via Azure CLI:**
```bash
# Get usage metrics
az monitor metrics list \
  --resource <resource-id> \
  --metric "Total Calls" "Total Tokens"
```

### Cost Optimization

```python
# Use cheaper models for simple tasks
CODE_GEN_MODEL = "azure/gpt-35-turbo-deployment"  # Cheaper
HYPOTHESIS_MODEL = "azure/gpt-4-deployment"  # More expensive

# Set token limits
MAX_TOKENS_CODE_GEN = 2000
MAX_TOKENS_HYPOTHESIS = 4000
```

## Troubleshooting

### Authentication Error

```bash
# Verify credentials
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# Test connection
curl -X POST \
  "$AZURE_OPENAI_ENDPOINT/openai/deployments/gpt-35-turbo-deployment/chat/completions?api-version=2024-02-15-preview" \
  -H "api-key: $AZURE_OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

### Deployment Not Found

```bash
# List available deployments
az cognitiveservices account deployment list \
  --name arl-openai \
  --resource-group arl-rg

# Verify deployment name in .env matches Azure
echo $AZURE_OPENAI_DEPLOYMENT_GPT4
```

### Rate Limit Exceeded

```python
# Add retry logic in settings.py
AZURE_OPENAI_RETRY_MAX_ATTEMPTS = 3
AZURE_OPENAI_RETRY_DELAY = 2  # seconds

# Reduce concurrency
MAX_CONCURRENT_EXPERIMENTS = 1
```

### Region Availability

```bash
# List available regions for Azure OpenAI
az account list-locations \
  --query "[?metadata.regionCategory=='Recommended'].{Name:name,DisplayName:displayName}" \
  --output table

# Create resource in different region
az cognitiveservices account create \
  --location eastus2  # or westeurope, etc.
```

## Security Best Practices

### Use Managed Identity

```bash
# Enable managed identity
az cognitiveservices account identity assign \
  --name arl-openai \
  --resource-group arl-rg

# Grant access
az role assignment create \
  --assignee <identity-principal-id> \
  --role "Cognitive Services User" \
  --scope <resource-id>
```

### Rotate Keys

```bash
# Regenerate keys periodically
az cognitiveservices account keys regenerate \
  --name arl-openai \
  --resource-group arl-rg \
  --key-name key1
```

### Network Security

```bash
# Restrict network access
az cognitiveservices account network-rule add \
  --name arl-openai \
  --resource-group arl-rg \
  --ip-address <your-ip>
```

## API Version Updates

Current supported versions:
- `2024-02-15-preview` (Latest)
- `2023-12-01-preview`
- `2023-05-15`

```bash
# Update API version
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"

# Or in .env
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Next Steps

- [Quickstart Guide](quickstart.md) - Run your first research cycle
- [User Guide](user-guide.md) - Complete documentation
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
