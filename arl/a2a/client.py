"""A2A Client wrappers for consuming remote agents."""

import logging
from typing import Any

from google.adk.a2a import RemoteA2aAgent

from arl.config.a2a_config import a2a_config, get_agent_url

logger = logging.getLogger(__name__)


class A2AAgentClient:
    """
    Client wrapper for interacting with remote A2A agents.

    This provides a unified interface for agent communication that works
    with both local and remote agents transparently.
    """

    def __init__(
        self,
        agent_name: str,
        service_url: str | None = None,
        timeout: int | None = None,
    ):
        """
        Initialize A2A agent client.

        Args:
            agent_name: Agent identifier (hypothesis, experiment, etc.)
            service_url: Optional service URL (defaults to config)
            timeout: Request timeout in seconds (defaults to config)
        """
        self.agent_name = agent_name
        self.service_url = service_url or self._get_service_url(agent_name)
        self.timeout = timeout or a2a_config.timeout_seconds

        # Remote A2A agent proxy
        self._remote_agent: RemoteA2aAgent | None = None
        self._initialized = False

    def _get_service_url(self, agent_name: str) -> str:
        """Get service URL from configuration."""
        # Check if custom URL is configured
        url_mapping = {
            "hypothesis": a2a_config.hypothesis_agent_url,
            "experiment": a2a_config.experiment_agent_url,
            "code_gen": a2a_config.code_gen_agent_url,
            "execution": a2a_config.execution_agent_url,
            "analysis": a2a_config.analysis_agent_url,
        }

        custom_url = url_mapping.get(agent_name)
        if custom_url:
            return custom_url

        # Default to local URL based on port allocation
        return get_agent_url(agent_name)

    async def initialize(self) -> None:
        """Initialize the remote agent connection."""
        if self._initialized:
            return

        logger.info(f"Initializing A2A client for {self.agent_name} at {self.service_url}")

        try:
            # Create remote agent proxy
            self._remote_agent = RemoteA2aAgent(
                service_url=self.service_url,
                timeout=self.timeout,
            )

            # Test connection by fetching agent card
            await self._remote_agent.get_agent_card()

            self._initialized = True
            logger.info(f"A2A client for {self.agent_name} initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize A2A client for {self.agent_name}: {e}")
            raise

    async def call_skill(
        self,
        skill_name: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Call a skill on the remote agent.

        Args:
            skill_name: Name of the skill to invoke
            input_data: Input parameters for the skill

        Returns:
            Skill execution result
        """
        if not self._initialized:
            await self.initialize()

        logger.debug(f"Calling skill '{skill_name}' on {self.agent_name}")

        try:
            result = await self._remote_agent.call_skill(
                skill_name=skill_name,
                input_data=input_data,
            )
            return result

        except Exception as e:
            logger.error(f"Failed to call skill '{skill_name}' on {self.agent_name}: {e}")
            raise

    async def get_agent_card(self) -> dict[str, Any]:
        """Get the agent card from the remote agent."""
        if not self._initialized:
            await self.initialize()

        return await self._remote_agent.get_agent_card()

    async def close(self) -> None:
        """Close the client connection."""
        if self._remote_agent:
            await self._remote_agent.close()
        self._initialized = False


class A2AAgentFactory:
    """
    Factory for creating agent clients based on deployment mode.

    This enables transparent switching between local and remote agents
    based on configuration.
    """

    @staticmethod
    async def create_agent_client(
        agent_name: str,
    ) -> A2AAgentClient | Any:
        """
        Create an agent client based on deployment mode.

        Args:
            agent_name: Agent identifier

        Returns:
            Agent client (A2AAgentClient for remote, local agent for local mode)
        """
        if a2a_config.deployment_mode == "local":
            # Return local agent instance
            return A2AAgentFactory._create_local_agent(agent_name)

        elif a2a_config.deployment_mode == "remote":
            # Return A2A client for remote agent
            client = A2AAgentClient(agent_name)
            await client.initialize()
            return client

        elif a2a_config.deployment_mode == "hybrid":
            # Check if custom URL is configured for this agent
            url_mapping = {
                "hypothesis": a2a_config.hypothesis_agent_url,
                "experiment": a2a_config.experiment_agent_url,
                "code_gen": a2a_config.code_gen_agent_url,
                "execution": a2a_config.execution_agent_url,
                "analysis": a2a_config.analysis_agent_url,
            }

            if url_mapping.get(agent_name):
                # Remote agent
                client = A2AAgentClient(agent_name)
                await client.initialize()
                return client
            else:
                # Local agent
                return A2AAgentFactory._create_local_agent(agent_name)

        else:
            raise ValueError(f"Unknown deployment mode: {a2a_config.deployment_mode}")

    @staticmethod
    def _create_local_agent(agent_name: str) -> Any:
        """Create a local agent instance."""
        from arl.adk_agents.analysis.agent import create_analysis_agent
        from arl.adk_agents.code_gen.agent import create_code_generator
        from arl.adk_agents.execution.agent import create_execution_engine
        from arl.adk_agents.experiment.agent import create_experiment_designer
        from arl.adk_agents.hypothesis.agent import create_hypothesis_agent

        agents = {
            "hypothesis": create_hypothesis_agent,
            "experiment": create_experiment_designer,
            "code_gen": create_code_generator,
            "execution": create_execution_engine,
            "analysis": create_analysis_agent,
        }

        factory_func = agents.get(agent_name)
        if not factory_func:
            raise ValueError(f"Unknown agent: {agent_name}")

        return factory_func()
