"""A2A (Agent-to-Agent) protocol integration for ARL."""

from arl.a2a.agent_cards import (
    ANALYSIS_AGENT_CARD,
    CODE_GENERATOR_CARD,
    EXECUTION_ENGINE_CARD,
    EXPERIMENT_DESIGNER_CARD,
    HYPOTHESIS_AGENT_CARD,
    AgentCard,
    get_agent_card,
)
from arl.a2a.server import A2AServerWrapper, create_a2a_server

__all__ = [
    "AgentCard",
    "get_agent_card",
    "HYPOTHESIS_AGENT_CARD",
    "EXPERIMENT_DESIGNER_CARD",
    "CODE_GENERATOR_CARD",
    "EXECUTION_ENGINE_CARD",
    "ANALYSIS_AGENT_CARD",
    "A2AServerWrapper",
    "create_a2a_server",
]
