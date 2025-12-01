"""A2A Protocol configuration for agent-to-agent communication."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class A2AConfig(BaseSettings):
    """
    Configuration for A2A (Agent-to-Agent) protocol.

    A2A enables standardized communication between agents using JSON-RPC 2.0
    over HTTP(S), allowing agents to run as independent services.
    """

    # A2A Server Settings
    enabled: bool = Field(
        default=False,
        description="Enable A2A protocol for agent communication",
    )

    host: str = Field(
        default="0.0.0.0",
        description="Host address for A2A server",
    )

    base_port: int = Field(
        default=8100,
        description="Base port for A2A servers (each agent gets base_port + offset)",
    )

    # Authentication Settings
    auth_scheme: Literal["none", "bearer", "api_key", "oauth2"] = Field(
        default="none",
        description="Authentication scheme for A2A communication",
    )

    api_key: str | None = Field(
        default=None,
        description="API key for authentication (when auth_scheme=api_key)",
    )

    bearer_token: str | None = Field(
        default=None,
        description="Bearer token for authentication (when auth_scheme=bearer)",
    )

    # Agent Discovery Settings
    agent_cards_dir: str = Field(
        default="./data/agent_cards",
        description="Directory to store agent card JSON files",
    )

    # Deployment Mode
    deployment_mode: Literal["local", "remote", "hybrid"] = Field(
        default="local",
        description=(
            "Deployment mode: "
            "'local' = all agents in same process, "
            "'remote' = agents as separate services, "
            "'hybrid' = configurable per agent"
        ),
    )

    # Agent Endpoints (for remote mode)
    hypothesis_agent_url: str | None = Field(
        default=None,
        description="URL for remote hypothesis agent (if deployment_mode=remote/hybrid)",
    )

    experiment_agent_url: str | None = Field(
        default=None,
        description="URL for remote experiment designer agent",
    )

    code_gen_agent_url: str | None = Field(
        default=None,
        description="URL for remote code generator agent",
    )

    execution_agent_url: str | None = Field(
        default=None,
        description="URL for remote execution engine agent",
    )

    analysis_agent_url: str | None = Field(
        default=None,
        description="URL for remote analysis agent",
    )

    # Performance Settings
    timeout_seconds: int = Field(
        default=300,
        description="Timeout for A2A requests in seconds",
    )

    max_retries: int = Field(
        default=3,
        description="Maximum retries for failed A2A requests",
    )

    class Config:
        env_prefix = "ARL_A2A_"
        env_file = ".env"


# Global A2A configuration instance
a2a_config = A2AConfig()


# Port allocation for agents (base_port + offset)
AGENT_PORT_OFFSETS = {
    "hypothesis": 0,  # 8100
    "experiment": 1,  # 8101
    "code_gen": 2,  # 8102
    "execution": 3,  # 8103
    "analysis": 4,  # 8104
}


def get_agent_port(agent_name: str) -> int:
    """Get the port number for a specific agent."""
    offset = AGENT_PORT_OFFSETS.get(agent_name, 0)
    return a2a_config.base_port + offset


def get_agent_url(agent_name: str) -> str:
    """Get the full URL for a specific agent."""
    port = get_agent_port(agent_name)
    return f"http://{a2a_config.host}:{port}"
