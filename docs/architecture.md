# ARL Architecture

## System Overview

ARL is a multi-agent system built on Google ADK for autonomous scientific research automation.

```
User Interface (CLI/API/Web)
         ↓
┌────────────────────────────────────┐
│    Orchestrator Agent (ADK)        │
│  • Task routing & coordination     │
│  • Session & context management    │
│  • Human interaction checkpoints   │
└────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────┐
│           Multi-Agent System (ADK)              │
├─────────────────────────────────────────────────┤
│  Literature Agent    │  Research Execution      │
│  • Paper ingestion   │  • Orchestrates stages   │
│  • Knowledge extract │  • Workflow coordination │
│  • Gap identification│                          │
│                      │                          │
│  Hypothesis Agent    │  Experiment Designer     │
│  • Generate hypoths  │  • Protocol design       │
│  • Ranking & scoring │  • Parameter specs       │
│                      │                          │
│  Code Generator      │  Execution Engine        │
│  • Python generation │  • Docker sandbox        │
│  • Validation        │  • Resource management   │
│                      │                          │
│  Analysis Agent                                 │
│  • Statistical analysis                         │
│  • Hypothesis validation                        │
│  • Recommendations                              │
└─────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────┐
│         Storage & Memory Layer                  │
│  • SQLite/Cloud SQL (metadata)                  │
│  • Filesystem/Cloud Storage (artifacts)         │
│  • Vertex AI Memory Bank (sessions)             │
└─────────────────────────────────────────────────┘
```

## Core Components

### 1. Agents (ADK-based)

**Orchestrator Agent**
- Routes tasks to specialist agents
- Maintains global context & session state
- Handles human-in-the-loop checkpoints

**Literature Agent**
- Paper ingestion (arXiv, PubMed, manual)
- PDF parsing & knowledge extraction
- Research gap identification

**Hypothesis Agent**
- Generates testable hypotheses from gaps
- Ranks by feasibility/novelty/impact
- Grounds in literature

**Experiment Designer Agent**
- Creates experimental protocols
- Defines parameters & validation criteria
- Estimates resource requirements

**Code Generator Agent**
- Generates Python code for experiments
- Uses scientific Python stack
- Validates syntax, dependencies, security

**Execution Engine**
- Docker sandbox isolation
- Resource monitoring & limits
- Result & artifact capture

**Analysis Agent**
- Statistical analysis of results
- Hypothesis validation (supported/refuted/inconclusive)
- Next step recommendations

### 2. Data Models

**Project**
```python
{
  "project_id": "uuid",
  "name": "string",
  "domain": "cs|biology|physics|general",
  "objectives": "string",
  "sessions": ["session_ids"],
  "papers": ["paper_ids"]
}
```

**Session**
```python
{
  "session_id": "uuid",
  "project_id": "uuid",
  "status": "active|paused|completed",
  "state": "dict (ADK state)",
  "experiments": ["experiment_ids"]
}
```

**Experiment**
```python
{
  "experiment_id": "uuid",
  "hypothesis": "string",
  "code": "string",
  "status": "pending|running|completed|failed",
  "results": "dict",
  "artifacts": ["files"],
  "analysis": "dict"
}
```

## Technology Stack

**Core Framework**
- Google ADK 1.0+ (agent orchestration)
- Python 3.10+

**LLM Integration**
- LiteLLM (multi-provider: Google/OpenAI/Anthropic)
- Vertex AI (Google Cloud)

**Execution**
- Docker (sandboxed experiments)
- Scientific Python: NumPy, pandas, scikit-learn, PyTorch

**Storage**
- SQLite (local) / Cloud SQL (cloud)
- Filesystem / Cloud Storage (artifacts)
- Vertex AI Memory Bank (sessions)

## Agent Communication

### A2A Protocol Support

ARL supports the **A2A (Agent-to-Agent) Protocol** for standardized agent communication:

- **Local Mode**: Agents run in same process (no network overhead)
- **Remote Mode**: Agents as independent microservices using JSON-RPC 2.0/HTTP
- **Hybrid Mode**: Mix of local and remote agents based on configuration

See [A2A Protocol Documentation](a2a-protocol.md) for detailed information.

### Communication Patterns

**Local (Default)**:
```
Orchestrator → Direct Method Call → Hypothesis Agent
```

**A2A Remote**:
```
Orchestrator → HTTP Request → A2A Server (Hypothesis Agent) → HTTP Response
```

**Agent Discovery**:
Each agent exposes an "Agent Card" (JSON metadata) describing:
- Available skills and capabilities
- Input/output schemas
- Service endpoint
- Authentication requirements

## Deployment Options

### Local Deployment
- In-memory services
- SQLite database
- Local LLM support (Ollama)
- Docker execution
- **A2A**: Disabled (direct method calls)

### Cloud Deployment (GCP)
- Vertex AI Agent Engine
- Cloud Run (agent services)
- Cloud SQL (metadata)
- Cloud Storage (artifacts)
- IAM-based security
- **A2A**: Enabled (microservices architecture)

### Hybrid Deployment
- Configuration-based agent placement
- Transparent local ↔ cloud communication
- Encrypted agent-to-agent channels
- **A2A**: Hybrid mode (mix of local/remote)

### Microservices Deployment (A2A)
- Each agent as independent HTTP service
- Load balancing and auto-scaling per agent
- Independent deployment and versioning
- Cross-platform agent integration (ADK, LangGraph, etc.)

## Research Workflow

```
1. User Request
   ↓
2. Literature Review (optional)
   → Papers ingested & analyzed
   → Research gaps identified
   ↓
3. Hypothesis Generation
   → 3-5 testable hypotheses
   → Ranked by feasibility/novelty
   ↓
4. Experiment Design
   → Protocol specification
   → Python code generation
   → Validation
   ↓
5. Execution
   → Docker sandbox
   → Result collection
   ↓
6. Analysis
   → Statistical validation
   → Hypothesis outcome
   → Recommendations
   ↓
7. Iteration (optional)
   → Refine based on results
```

## Security Architecture

**Execution Isolation**
- Docker containers (no privileged access)
- Resource limits (CPU, memory, time)
- Filesystem isolation
- Network isolation (no internet by default)

**Code Validation**
- Static analysis (dangerous patterns)
- Dependency whitelisting
- User review checkpoints

**Data Privacy**
- Encrypted storage (cloud)
- TLS communication
- Local deployment option for sensitive research

## Extensibility

**Plugin Architecture**
- New agent types
- Custom tools (MCP integration)
- Domain-specific templates
- Language generators (future: R, Julia)

**Tool Integration**
- MCP (Model Context Protocol)
- Custom API integrations
- Lab equipment (future)
