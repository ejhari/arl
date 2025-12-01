"""Tests for A2A (Agent-to-Agent) protocol integration."""

import pytest

from arl.a2a.agent_cards import (
    ANALYSIS_AGENT_CARD,
    CODE_GENERATOR_CARD,
    EXECUTION_ENGINE_CARD,
    EXPERIMENT_DESIGNER_CARD,
    HYPOTHESIS_AGENT_CARD,
    AgentCard,
    get_agent_card,
)
from arl.a2a.client import A2AAgentClient, A2AAgentFactory
from arl.a2a.server import A2AServerWrapper, create_a2a_server
from arl.adk_agents.hypothesis.agent import create_hypothesis_agent
from arl.config.a2a_config import a2a_config, get_agent_port, get_agent_url


class TestAgentCards:
    """Test agent card definitions and retrieval."""

    def test_agent_card_structure(self):
        """Test that agent cards have required fields."""
        agent_cards = [
            HYPOTHESIS_AGENT_CARD,
            EXPERIMENT_DESIGNER_CARD,
            CODE_GENERATOR_CARD,
            EXECUTION_ENGINE_CARD,
            ANALYSIS_AGENT_CARD,
        ]

        for card in agent_cards:
            assert isinstance(card, AgentCard)
            assert card.name
            assert card.display_name
            assert card.description
            assert card.version
            assert card.capabilities
            assert card.capabilities.skills
            assert len(card.capabilities.skills) > 0
            assert card.protocol_version == "0.3"
            assert card.provider == "ARL"

    def test_agent_card_skills(self):
        """Test that each agent card has properly defined skills."""
        # Hypothesis agent
        assert len(HYPOTHESIS_AGENT_CARD.capabilities.skills) == 1
        hyp_skill = HYPOTHESIS_AGENT_CARD.capabilities.skills[0]
        assert hyp_skill.name == "generate_hypotheses"
        assert "literature_summary" in hyp_skill.input_schema["properties"]
        assert "research_gap" in hyp_skill.input_schema["properties"]

        # Code generator
        assert len(CODE_GENERATOR_CARD.capabilities.skills) == 1
        code_skill = CODE_GENERATOR_CARD.capabilities.skills[0]
        assert code_skill.name == "generate_code"
        assert "experiment_design" in code_skill.input_schema["properties"]

    def test_get_agent_card(self):
        """Test retrieving agent cards with service endpoint."""
        service_endpoint = "http://localhost:8100"
        card = get_agent_card("hypothesis", service_endpoint)

        assert card.name == "hypothesis_agent"
        assert card.service_endpoint == service_endpoint

    def test_get_agent_card_unknown_agent(self):
        """Test error handling for unknown agent."""
        with pytest.raises(ValueError, match="Unknown agent"):
            get_agent_card("unknown_agent", "http://localhost:8100")


class TestA2AConfiguration:
    """Test A2A configuration and utilities."""

    def test_agent_port_allocation(self):
        """Test that each agent gets a unique port."""
        agents = ["hypothesis", "experiment", "code_gen", "execution", "analysis"]
        ports = [get_agent_port(agent) for agent in agents]

        # All ports should be unique
        assert len(ports) == len(set(ports))

        # All ports should be in valid range
        for port in ports:
            assert 1024 < port < 65535

    def test_agent_url_generation(self):
        """Test agent URL generation."""
        url = get_agent_url("hypothesis")
        port = get_agent_port("hypothesis")

        assert f":{port}" in url
        assert url.startswith("http://")


class TestA2AServer:
    """Test A2A server wrapper functionality."""

    def test_server_creation(self):
        """Test creating an A2A server wrapper."""
        agent = create_hypothesis_agent()
        server = create_a2a_server(agent, "hypothesis")

        assert isinstance(server, A2AServerWrapper)
        assert server.agent_name == "hypothesis"
        assert server.host == a2a_config.host
        assert server.port == get_agent_port("hypothesis")
        assert not server.is_running

    def test_server_agent_card(self):
        """Test server agent card generation."""
        agent = create_hypothesis_agent()
        server = create_a2a_server(agent, "hypothesis")

        card = server.get_agent_card()
        assert isinstance(card, AgentCard)
        assert card.name == "hypothesis_agent"
        assert card.service_endpoint == server.service_endpoint


class TestA2AClient:
    """Test A2A client functionality."""

    def test_client_creation(self):
        """Test creating an A2A client."""
        client = A2AAgentClient("hypothesis")

        assert client.agent_name == "hypothesis"
        assert client.service_url == get_agent_url("hypothesis")
        assert client.timeout == a2a_config.timeout_seconds
        assert not client._initialized

    def test_client_custom_url(self):
        """Test client with custom service URL."""
        custom_url = "http://custom-host:9999"
        client = A2AAgentClient("hypothesis", service_url=custom_url)

        assert client.service_url == custom_url


class TestA2AAgentFactory:
    """Test A2A agent factory for deployment mode handling."""

    def test_create_local_agent(self, monkeypatch):
        """Test creating local agent when A2A is disabled."""
        # Set deployment mode to local
        monkeypatch.setattr(a2a_config, "deployment_mode", "local")

        agent = A2AAgentFactory._create_local_agent("hypothesis")
        assert agent is not None
        # Should be a local agent instance, not an A2A client
        assert not isinstance(agent, A2AAgentClient)

    def test_create_local_agent_unknown(self):
        """Test error handling for unknown agent in factory."""
        with pytest.raises(ValueError, match="Unknown agent"):
            A2AAgentFactory._create_local_agent("unknown_agent")


class TestA2AIntegration:
    """Integration tests for A2A protocol (require running servers)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_hypothesis_generation(self):
        """
        End-to-end test of hypothesis generation through A2A.

        Note: This test requires A2A servers to be running.
        Run with: arl a2a start --agent all
        """
        # This is a placeholder for actual integration tests
        # that would require running A2A servers
        pytest.skip("Requires running A2A servers - run manually")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_orchestrator_with_a2a(self):
        """
        Test orchestrator using A2A communication.

        Note: This test requires A2A servers to be running.
        """
        pytest.skip("Requires running A2A servers - run manually")


# Pytest configuration for integration tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires running services)"
    )
