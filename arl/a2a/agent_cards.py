"""Agent Card definitions for A2A protocol discovery."""

from typing import Any

from pydantic import BaseModel, Field


class AgentSkill(BaseModel):
    """Definition of a specific skill an agent can perform."""

    name: str = Field(..., description="Unique identifier for the skill")
    description: str = Field(..., description="Human-readable description of the skill")
    input_schema: dict[str, Any] = Field(
        ..., description="JSON schema for skill input parameters"
    )
    output_schema: dict[str, Any] = Field(
        ..., description="JSON schema for skill output"
    )


class AgentCapabilities(BaseModel):
    """Capabilities and metadata for an agent."""

    skills: list[AgentSkill] = Field(..., description="List of skills this agent provides")
    supported_modalities: list[str] = Field(
        default=["text"], description="Modalities supported (text, audio, video, etc.)"
    )
    max_concurrent_tasks: int = Field(
        default=5, description="Maximum concurrent tasks this agent can handle"
    )
    average_response_time_ms: int | None = Field(
        default=None, description="Average response time in milliseconds"
    )


class AgentAuthentication(BaseModel):
    """Authentication requirements for the agent."""

    type: str = Field(..., description="Authentication type (none, bearer, api_key, oauth2)")
    token_endpoint: str | None = Field(
        default=None, description="Token endpoint URL for OAuth2"
    )
    scopes: list[str] = Field(default=[], description="Required OAuth2 scopes")


class AgentCard(BaseModel):
    """
    Agent Card - JSON metadata describing an A2A agent.

    This follows the A2A protocol specification for agent discovery.
    """

    # Identity
    name: str = Field(..., description="Unique agent identifier")
    display_name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Agent purpose and responsibilities")
    version: str = Field(..., description="Agent version (semver)")

    # Capabilities
    capabilities: AgentCapabilities = Field(..., description="Agent capabilities")

    # Connection Info
    service_endpoint: str = Field(..., description="Base URL for A2A communication")
    protocol_version: str = Field(
        default="0.3", description="A2A protocol version supported"
    )

    # Authentication
    authentication: AgentAuthentication = Field(
        ..., description="Authentication requirements"
    )

    # Metadata
    provider: str = Field(default="ARL", description="Organization providing this agent")
    tags: list[str] = Field(default=[], description="Tags for categorization")


# Agent Card Definitions for ARL Agents

HYPOTHESIS_AGENT_CARD = AgentCard(
    name="hypothesis_agent",
    display_name="Hypothesis Generation Agent",
    description="Generates testable research hypotheses from literature analysis and research gaps",
    version="0.1.0",
    capabilities=AgentCapabilities(
        skills=[
            AgentSkill(
                name="generate_hypotheses",
                description="Generate 3-5 testable research hypotheses based on literature review",
                input_schema={
                    "type": "object",
                    "properties": {
                        "literature_summary": {
                            "type": "string",
                            "description": "Summary of reviewed literature",
                        },
                        "research_gap": {
                            "type": "string",
                            "description": "Identified research gap",
                        },
                        "domain": {
                            "type": "string",
                            "description": "Scientific domain (cs, biology, physics, general)",
                        },
                    },
                    "required": ["literature_summary", "research_gap", "domain"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "raw_output": {"type": "string"},
                        "model_used": {"type": "string"},
                        "tokens_used": {"type": "integer"},
                    },
                },
            )
        ],
        supported_modalities=["text"],
        max_concurrent_tasks=3,
    ),
    service_endpoint="",  # Will be populated at runtime
    authentication=AgentAuthentication(type="none"),
    provider="ARL",
    tags=["research", "hypothesis", "scientific"],
)

EXPERIMENT_DESIGNER_CARD = AgentCard(
    name="experiment_designer",
    display_name="Experiment Designer Agent",
    description="Designs experimental protocols and parameters for hypothesis testing",
    version="0.1.0",
    capabilities=AgentCapabilities(
        skills=[
            AgentSkill(
                name="design_experiment",
                description="Create experimental protocol and parameter specification",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hypothesis": {"type": "string", "description": "Hypothesis to test"},
                        "domain": {"type": "string", "description": "Scientific domain"},
                    },
                    "required": ["hypothesis", "domain"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "raw_output": {"type": "string"},
                        "model_used": {"type": "string"},
                        "tokens_used": {"type": "integer"},
                    },
                },
            )
        ],
        supported_modalities=["text"],
        max_concurrent_tasks=3,
    ),
    service_endpoint="",
    authentication=AgentAuthentication(type="none"),
    provider="ARL",
    tags=["research", "experiment", "design"],
)

CODE_GENERATOR_CARD = AgentCard(
    name="code_generator",
    display_name="Code Generator Agent",
    description="Generates production-ready Python code for scientific experiments",
    version="0.1.0",
    capabilities=AgentCapabilities(
        skills=[
            AgentSkill(
                name="generate_code",
                description="Generate validated Python experiment code",
                input_schema={
                    "type": "object",
                    "properties": {
                        "experiment_design": {
                            "type": "object",
                            "description": "Experiment design specification",
                        },
                        "domain": {"type": "string", "description": "Scientific domain"},
                    },
                    "required": ["experiment_design", "domain"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "validation": {"type": "object"},
                        "dependencies": {"type": "array"},
                        "model_used": {"type": "string"},
                        "tokens_used": {"type": "integer"},
                    },
                },
            )
        ],
        supported_modalities=["text"],
        max_concurrent_tasks=2,
    ),
    service_endpoint="",
    authentication=AgentAuthentication(type="none"),
    provider="ARL",
    tags=["code", "python", "generation"],
)

EXECUTION_ENGINE_CARD = AgentCard(
    name="execution_engine",
    display_name="Execution Engine Agent",
    description="Executes experiments in isolated Docker sandbox with resource monitoring",
    version="0.1.0",
    capabilities=AgentCapabilities(
        skills=[
            AgentSkill(
                name="execute_experiment",
                description="Execute Python code in Docker sandbox",
                input_schema={
                    "type": "object",
                    "properties": {
                        "experiment_id": {
                            "type": "string",
                            "description": "Unique experiment identifier",
                        },
                        "code": {"type": "string", "description": "Python code to execute"},
                    },
                    "required": ["experiment_id", "code"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "stdout": {"type": "string"},
                        "stderr": {"type": "string"},
                        "exit_code": {"type": "integer"},
                        "artifacts": {"type": "array"},
                        "experiment_id": {"type": "string"},
                    },
                },
            )
        ],
        supported_modalities=["text"],
        max_concurrent_tasks=5,
        average_response_time_ms=30000,  # Can be long-running
    ),
    service_endpoint="",
    authentication=AgentAuthentication(type="none"),
    provider="ARL",
    tags=["execution", "docker", "sandbox"],
)

ANALYSIS_AGENT_CARD = AgentCard(
    name="analysis_agent",
    display_name="Analysis Agent",
    description="Performs statistical analysis and hypothesis validation",
    version="0.1.0",
    capabilities=AgentCapabilities(
        skills=[
            AgentSkill(
                name="analyze_results",
                description="Analyze experiment results and validate hypothesis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hypothesis": {"type": "string", "description": "Original hypothesis"},
                        "experiment_design": {
                            "type": "object",
                            "description": "Experiment design",
                        },
                        "execution_results": {
                            "type": "object",
                            "description": "Execution results",
                        },
                        "domain": {"type": "string", "description": "Scientific domain"},
                    },
                    "required": ["hypothesis", "experiment_design", "execution_results", "domain"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "raw_output": {"type": "string"},
                        "model_used": {"type": "string"},
                        "tokens_used": {"type": "integer"},
                    },
                },
            )
        ],
        supported_modalities=["text"],
        max_concurrent_tasks=3,
    ),
    service_endpoint="",
    authentication=AgentAuthentication(type="none"),
    provider="ARL",
    tags=["analysis", "statistics", "validation"],
)


def get_agent_card(agent_name: str, service_endpoint: str) -> AgentCard:
    """Get an agent card with the service endpoint populated."""
    cards = {
        "hypothesis": HYPOTHESIS_AGENT_CARD,
        "experiment": EXPERIMENT_DESIGNER_CARD,
        "code_gen": CODE_GENERATOR_CARD,
        "execution": EXECUTION_ENGINE_CARD,
        "analysis": ANALYSIS_AGENT_CARD,
    }

    card = cards.get(agent_name)
    if not card:
        raise ValueError(f"Unknown agent: {agent_name}")

    # Create a copy with the service endpoint
    card_dict = card.model_dump()
    card_dict["service_endpoint"] = service_endpoint
    return AgentCard(**card_dict)
