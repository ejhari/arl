# A2A Protocol Integration

## Overview

ARL now supports the **A2A (Agent-to-Agent) Protocol**, Google's open standard for agent-to-agent communication. This enables agents to communicate using a standardized protocol (JSON-RPC 2.0 over HTTP/HTTPS), allowing for flexible deployment architectures from monolithic to fully distributed microservices.

## What is A2A?

The A2A protocol is an open standard for agent interoperability that provides:

- **Standardized Communication**: JSON-RPC 2.0 over HTTP(S) for reliable, secure agent-to-agent interaction
- **Agent Discovery**: JSON "Agent Cards" describing capabilities, skills, and connection info
- **Cross-Platform**: Language and framework agnostic (works with ADK, LangGraph, Crew.ai, etc.)
- **Enterprise-Ready**: Built-in support for authentication, authorization, and security
- **Flexible Deployment**: Run agents locally or as distributed microservices

## Architecture

### Deployment Modes

ARL supports three deployment modes for A2A:

#### 1. Local Mode (Default)
All agents run in the same Python process. No A2A protocol overhead.

```bash
# .env configuration
ARL_A2A_ENABLED=false
```

**Use Cases:**
- Local development
- Simple single-machine deployments
- Testing and debugging

#### 2. Remote Mode
All agents run as independent A2A servers with network communication.

```bash
# .env configuration
ARL_A2A_ENABLED=true
ARL_A2A_DEPLOYMENT_MODE=remote
ARL_A2A_BASE_PORT=8100
```

**Use Cases:**
- Microservices architecture
- Distributed deployment across machines
- Scalability and fault isolation
- Independent agent scaling

#### 3. Hybrid Mode
Mix of local and remote agents. Specify custom URLs for remote agents.

```bash
# .env configuration
ARL_A2A_ENABLED=true
ARL_A2A_DEPLOYMENT_MODE=hybrid
ARL_A2A_HYPOTHESIS_AGENT_URL=http://remote-server:8100
ARL_A2A_CODE_GEN_AGENT_URL=http://another-server:8102
# Other agents will run locally
```

**Use Cases:**
- Gradual migration to microservices
- Resource-intensive agents on separate servers
- Heterogeneous infrastructure

### Agent Port Allocation

In remote/hybrid mode, each agent gets a dedicated port:

| Agent | Port Offset | Default Port | Purpose |
|-------|-------------|--------------|---------|
| Hypothesis Agent | 0 | 8100 | Generate research hypotheses |
| Experiment Designer | 1 | 8101 | Design experimental protocols |
| Code Generator | 2 | 8102 | Generate Python experiment code |
| Execution Engine | 3 | 8103 | Execute experiments in Docker |
| Analysis Agent | 4 | 8104 | Analyze results and validate hypotheses |

Base port is configurable via `ARL_A2A_BASE_PORT` (default: 8100).

## Agent Cards

Each agent exposes an **Agent Card** - a JSON document describing its capabilities:

```json
{
  "name": "hypothesis_agent",
  "display_name": "Hypothesis Generation Agent",
  "description": "Generates testable research hypotheses from literature analysis",
  "version": "0.1.0",
  "protocol_version": "0.3",
  "service_endpoint": "http://localhost:8100",
  "capabilities": {
    "skills": [
      {
        "name": "generate_hypotheses",
        "description": "Generate 3-5 testable research hypotheses",
        "input_schema": { ... },
        "output_schema": { ... }
      }
    ],
    "supported_modalities": ["text"],
    "max_concurrent_tasks": 3
  },
  "authentication": {
    "type": "none"
  },
  "provider": "ARL",
  "tags": ["research", "hypothesis", "scientific"]
}
```

## Getting Started

### 1. Enable A2A Protocol

```bash
# Create/edit .env file
echo "ARL_A2A_ENABLED=true" >> .env
echo "ARL_A2A_DEPLOYMENT_MODE=remote" >> .env
```

### 2. Check Configuration

```bash
arl a2a status
```

Example output:
```
A2A Protocol Configuration

Setting          Value
Enabled          True
Deployment Mode  remote
Host             0.0.0.0
Base Port        8100
Auth Scheme      none
Timeout          300s

Agent Endpoints

Agent        Port    URL
hypothesis   8100    http://0.0.0.0:8100
experiment   8101    http://0.0.0.0:8101
code_gen     8102    http://0.0.0.0:8102
execution    8103    http://0.0.0.0:8103
analysis     8104    http://0.0.0.0:8104
```

### 3. Start A2A Servers

**Start all agents:**
```bash
arl a2a start --agent all
```

**Start specific agent:**
```bash
arl a2a start --agent hypothesis
```

**In separate terminals for different agents:**
```bash
# Terminal 1
arl a2a start --agent hypothesis

# Terminal 2
arl a2a start --agent experiment

# Terminal 3
arl a2a start --agent code_gen
```

### 4. Test Agent Connection

```bash
arl a2a test --agent hypothesis
```

Example output:
```
Testing connection to hypothesis agent...
✓ Successfully connected to hypothesis

Agent Card:
Name: hypothesis_agent
Display Name: Hypothesis Generation Agent
Description: Generates testable research hypotheses from literature analysis
Version: 0.1.0
Protocol Version: 0.3
```

### 5. Run Research with A2A

Once servers are running, use ARL normally:

```bash
arl research run --project <project-id> --request "Test hypothesis" --auto
```

The orchestrator will automatically use A2A protocol for agent communication.

## Configuration Reference

### Environment Variables

```bash
# Core A2A Settings
ARL_A2A_ENABLED=true                    # Enable A2A protocol
ARL_A2A_DEPLOYMENT_MODE=remote          # local|remote|hybrid
ARL_A2A_HOST=0.0.0.0                    # Server host
ARL_A2A_BASE_PORT=8100                  # Base port for agents

# Authentication
ARL_A2A_AUTH_SCHEME=none                # none|bearer|api_key|oauth2
ARL_A2A_API_KEY=your-api-key           # API key (if auth_scheme=api_key)
ARL_A2A_BEARER_TOKEN=your-token        # Bearer token (if auth_scheme=bearer)

# Performance
ARL_A2A_TIMEOUT_SECONDS=300             # Request timeout
ARL_A2A_MAX_RETRIES=3                   # Max retry attempts

# Agent Endpoints (Hybrid Mode)
ARL_A2A_HYPOTHESIS_AGENT_URL=http://remote:8100
ARL_A2A_EXPERIMENT_AGENT_URL=http://remote:8101
ARL_A2A_CODE_GEN_AGENT_URL=http://remote:8102
ARL_A2A_EXECUTION_AGENT_URL=http://remote:8103
ARL_A2A_ANALYSIS_AGENT_URL=http://remote:8104

# Discovery
ARL_A2A_AGENT_CARDS_DIR=./data/agent_cards
```

### Python Configuration

```python
from arl.config.a2a_config import a2a_config

# Check if A2A is enabled
if a2a_config.enabled:
    print(f"A2A Mode: {a2a_config.deployment_mode}")
    print(f"Base Port: {a2a_config.base_port}")
```

## CLI Commands

### `arl a2a status`
Show current A2A configuration and agent endpoints.

### `arl a2a start`
Start A2A server(s) for agents.

**Options:**
- `--agent [hypothesis|experiment|code_gen|execution|analysis|all]`: Agent to start (default: all)
- `--detach`: Run in background (not yet implemented)

**Examples:**
```bash
# Start all agents
arl a2a start

# Start specific agent
arl a2a start --agent hypothesis

# Start with custom settings (via environment)
ARL_A2A_BASE_PORT=9000 arl a2a start
```

### `arl a2a test`
Test connection to an A2A agent.

**Options:**
- `--agent [hypothesis|experiment|code_gen|execution|analysis]`: Agent to test (required)
- `--url URL`: Custom agent URL (optional)

**Examples:**
```bash
# Test local agent
arl a2a test --agent hypothesis

# Test remote agent
arl a2a test --agent hypothesis --url http://remote-server:8100
```

### `arl a2a enable`
Show instructions to enable A2A protocol.

### `arl a2a disable`
Show instructions to disable A2A protocol.

## Programmatic Usage

### Server-Side: Expose an Agent

```python
from arl.a2a import create_a2a_server
from arl.adk_agents.hypothesis.agent import create_hypothesis_agent

# Create agent
agent = create_hypothesis_agent()

# Create A2A server
server = create_a2a_server(agent, "hypothesis")

# Start server
await server.start()

# Server is now running at http://0.0.0.0:8100
# Keep it running
await server.serve_forever()
```

### Client-Side: Consume an Agent

```python
from arl.a2a.client import A2AAgentClient

# Create client
client = A2AAgentClient("hypothesis")

# Initialize connection
await client.initialize()

# Call agent skill
result = await client.call_skill(
    skill_name="generate_hypotheses",
    input_data={
        "literature_summary": "Recent advances in ML...",
        "research_gap": "Lack of theoretical understanding",
        "domain": "cs"
    }
)

# Close client
await client.close()
```

### Orchestrator Integration

The orchestrator automatically handles A2A based on configuration:

```python
from arl.adk_agents.orchestrator.agent import create_orchestrator

# Create orchestrator
orchestrator = create_orchestrator()

# Run workflow - uses A2A if enabled
result = await orchestrator.run(
    session_id="session-123",
    user_request="Generate hypotheses about...",
)

# Orchestrator automatically:
# - Uses local agents if A2A disabled
# - Uses A2A clients if A2A enabled
# - Handles mixed mode in hybrid deployment
```

## Deployment Patterns

### Pattern 1: Local Development
```bash
# .env
ARL_A2A_ENABLED=false

# All agents run in-process
arl research run --project <id> --request "..."
```

### Pattern 2: Single-Server Microservices
```bash
# .env
ARL_A2A_ENABLED=true
ARL_A2A_DEPLOYMENT_MODE=remote
ARL_A2A_HOST=0.0.0.0
ARL_A2A_BASE_PORT=8100

# Terminal 1: Start all A2A servers
arl a2a start

# Terminal 2: Run research (orchestrator connects to local A2A servers)
arl research run --project <id> --request "..."
```

### Pattern 3: Distributed Microservices
```bash
# Machine 1 (Orchestrator + Hypothesis Agent)
ARL_A2A_ENABLED=true
ARL_A2A_DEPLOYMENT_MODE=hybrid
ARL_A2A_CODE_GEN_AGENT_URL=http://machine2:8102
ARL_A2A_EXECUTION_AGENT_URL=http://machine3:8103

# Start local agents
arl a2a start --agent hypothesis

# Run orchestrator
arl research run --project <id> --request "..."

# Machine 2 (Code Generator)
arl a2a start --agent code_gen

# Machine 3 (Execution Engine)
arl a2a start --agent execution
```

### Pattern 4: Docker Compose

```yaml
version: '3.8'

services:
  hypothesis:
    build: .
    command: arl a2a start --agent hypothesis
    ports:
      - "8100:8100"
    environment:
      - ARL_A2A_ENABLED=true
      - ARL_A2A_HOST=0.0.0.0

  experiment:
    build: .
    command: arl a2a start --agent experiment
    ports:
      - "8101:8101"
    environment:
      - ARL_A2A_ENABLED=true
      - ARL_A2A_HOST=0.0.0.0

  code_gen:
    build: .
    command: arl a2a start --agent code_gen
    ports:
      - "8102:8102"
    environment:
      - ARL_A2A_ENABLED=true
      - ARL_A2A_HOST=0.0.0.0

  orchestrator:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - ARL_A2A_ENABLED=true
      - ARL_A2A_DEPLOYMENT_MODE=remote
      - ARL_A2A_HYPOTHESIS_AGENT_URL=http://hypothesis:8100
      - ARL_A2A_EXPERIMENT_AGENT_URL=http://experiment:8101
      - ARL_A2A_CODE_GEN_AGENT_URL=http://code_gen:8102
    depends_on:
      - hypothesis
      - experiment
      - code_gen
```

## Security

### Authentication

A2A supports multiple authentication schemes:

```bash
# No authentication (default, development only)
ARL_A2A_AUTH_SCHEME=none

# API Key authentication
ARL_A2A_AUTH_SCHEME=api_key
ARL_A2A_API_KEY=your-secret-key

# Bearer token authentication
ARL_A2A_AUTH_SCHEME=bearer
ARL_A2A_BEARER_TOKEN=your-bearer-token

# OAuth2 (future support)
ARL_A2A_AUTH_SCHEME=oauth2
```

### Network Security

For production deployments:

1. **Use HTTPS**: Deploy behind reverse proxy (nginx, Traefik) with TLS
2. **Firewall Rules**: Restrict agent ports to trusted networks
3. **VPC/Private Network**: Run agents in private network, expose only orchestrator
4. **API Gateway**: Use API gateway for rate limiting and authentication

## Troubleshooting

### Issue: Connection refused

**Symptom:**
```
Error: Connection refused when testing agent
```

**Solution:**
1. Ensure A2A server is running: `arl a2a start --agent hypothesis`
2. Check port availability: `netstat -tulpn | grep 8100`
3. Verify firewall settings
4. Check `ARL_A2A_HOST` is accessible from client

### Issue: Agent card not found

**Symptom:**
```
Error: Agent card not found for agent 'hypothesis'
```

**Solution:**
1. Verify agent is running: `arl a2a status`
2. Test connection: `arl a2a test --agent hypothesis`
3. Check logs for server startup errors

### Issue: Timeout errors

**Symptom:**
```
Error: Request timeout after 300 seconds
```

**Solution:**
1. Increase timeout: `ARL_A2A_TIMEOUT_SECONDS=600`
2. Check agent server logs for performance issues
3. Consider scaling agent resources

## Performance Considerations

### Network Latency

A2A introduces network overhead compared to local agents:

- **Local**: ~1ms agent invocation
- **A2A (same machine)**: ~10-50ms (HTTP overhead)
- **A2A (remote)**: Network latency + processing time

**Recommendation**: Use local mode for development, A2A for production scalability.

### Concurrent Requests

Each agent can handle concurrent requests based on `max_concurrent_tasks`:

```python
AgentCapabilities(
    max_concurrent_tasks=5,  # Handle 5 requests concurrently
    ...
)
```

Scale by running multiple agent instances behind a load balancer.

### Caching

A2A clients cache agent cards to reduce discovery overhead.

## Advanced Topics

### Custom Agent Cards

Create custom agent cards for new agents:

```python
from arl.a2a.agent_cards import AgentCard, AgentCapabilities, AgentSkill

custom_card = AgentCard(
    name="my_agent",
    display_name="My Custom Agent",
    description="Does custom research tasks",
    version="1.0.0",
    capabilities=AgentCapabilities(
        skills=[
            AgentSkill(
                name="custom_skill",
                description="My custom skill",
                input_schema={"type": "object", ...},
                output_schema={"type": "object", ...},
            )
        ]
    ),
    service_endpoint="http://localhost:8105",
    authentication=AgentAuthentication(type="none"),
)
```

### Monitoring and Observability

Integrate with OpenTelemetry for distributed tracing:

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter

# Configure tracing for A2A requests
# (Implementation depends on ADK OpenTelemetry support)
```

### Health Checks

Implement health check endpoints for orchestration systems:

```python
@app.get("/health")
async def health_check():
    """Health check for load balancer."""
    return {"status": "healthy"}
```

## Resources

- [A2A Protocol Specification](https://a2a-protocol.org/)
- [Google ADK A2A Documentation](https://google.github.io/adk-docs/a2a/)
- [A2A Protocol GitHub](https://github.com/a2aproject/A2A)
- [ARL Architecture Documentation](architecture.md)

## Changelog

### v0.1.0 (2025-01-XX)
- Initial A2A protocol integration
- Support for local, remote, and hybrid deployment modes
- Agent cards for all ARL agents
- CLI commands for A2A management
- Comprehensive documentation
