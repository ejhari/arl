"""A2A Server wrappers for exposing agents over the A2A protocol."""

import asyncio
import logging
from typing import Any

from google.adk import Agent
from google.adk.a2a import A2AServer

from arl.a2a.agent_cards import AgentCard, get_agent_card
from arl.config.a2a_config import a2a_config, get_agent_port, get_agent_url

logger = logging.getLogger(__name__)


class A2AServerWrapper:
    """
    Wrapper for exposing an ADK agent as an A2A server.

    This enables the agent to communicate with other agents using the
    standardized A2A (Agent-to-Agent) protocol over HTTP(S).
    """

    def __init__(
        self,
        agent: Agent,
        agent_name: str,
        host: str | None = None,
        port: int | None = None,
    ):
        """
        Initialize A2A server wrapper.

        Args:
            agent: The ADK agent to expose
            agent_name: Agent identifier (hypothesis, experiment, code_gen, etc.)
            host: Host address (defaults to config)
            port: Port number (defaults to config + offset)
        """
        self.agent = agent
        self.agent_name = agent_name
        self.host = host or a2a_config.host
        self.port = port or get_agent_port(agent_name)

        # Service endpoint
        self.service_endpoint = f"http://{self.host}:{self.port}"

        # Agent card
        self.agent_card = get_agent_card(agent_name, self.service_endpoint)

        # A2A server (will be created when starting)
        self._a2a_server: A2AServer | None = None
        self._running = False

    async def start(self) -> None:
        """Start the A2A server."""
        if self._running:
            logger.warning(f"A2A server for {self.agent_name} is already running")
            return

        logger.info(
            f"Starting A2A server for {self.agent_name} at {self.service_endpoint}"
        )

        try:
            # Create A2A server with the agent
            self._a2a_server = A2AServer(
                agent=self.agent,
                host=self.host,
                port=self.port,
                agent_card=self.agent_card.model_dump(),
            )

            # Start the server
            await self._a2a_server.start()
            self._running = True

            logger.info(f"A2A server for {self.agent_name} started successfully")

        except Exception as e:
            logger.error(f"Failed to start A2A server for {self.agent_name}: {e}")
            raise

    async def stop(self) -> None:
        """Stop the A2A server."""
        if not self._running or not self._a2a_server:
            return

        logger.info(f"Stopping A2A server for {self.agent_name}")

        try:
            await self._a2a_server.stop()
            self._running = False
            logger.info(f"A2A server for {self.agent_name} stopped successfully")

        except Exception as e:
            logger.error(f"Failed to stop A2A server for {self.agent_name}: {e}")
            raise

    async def serve_forever(self) -> None:
        """Start the server and keep it running."""
        await self.start()
        try:
            # Keep the server running
            while self._running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"Received shutdown signal for {self.agent_name}")
        finally:
            await self.stop()

    def get_agent_card(self) -> AgentCard:
        """Get the agent card for discovery."""
        return self.agent_card

    @property
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._running


def create_a2a_server(
    agent: Agent,
    agent_name: str,
    host: str | None = None,
    port: int | None = None,
) -> A2AServerWrapper:
    """
    Factory function to create an A2A server wrapper.

    Args:
        agent: The ADK agent to expose
        agent_name: Agent identifier
        host: Optional host address
        port: Optional port number

    Returns:
        A2AServerWrapper instance
    """
    return A2AServerWrapper(
        agent=agent,
        agent_name=agent_name,
        host=host,
        port=port,
    )


async def start_all_agent_servers() -> dict[str, A2AServerWrapper]:
    """
    Start A2A servers for all ARL agents.

    This is useful for microservices deployment where each agent
    runs as an independent service.

    Returns:
        Dictionary mapping agent names to their server wrappers
    """
    from arl.adk_agents.analysis.agent import create_analysis_agent
    from arl.adk_agents.code_gen.agent import create_code_generator
    from arl.adk_agents.execution.agent import create_execution_engine
    from arl.adk_agents.experiment.agent import create_experiment_designer
    from arl.adk_agents.hypothesis.agent import create_hypothesis_agent

    # Create all agents
    agents = {
        "hypothesis": create_hypothesis_agent(),
        "experiment": create_experiment_designer(),
        "code_gen": create_code_generator(),
        "execution": create_execution_engine(),
        "analysis": create_analysis_agent(),
    }

    # Create A2A servers
    servers = {}
    for agent_name, agent in agents.items():
        server = create_a2a_server(agent, agent_name)
        servers[agent_name] = server

    # Start all servers
    start_tasks = [server.start() for server in servers.values()]
    await asyncio.gather(*start_tasks)

    logger.info("All A2A agent servers started successfully")
    return servers


async def stop_all_agent_servers(
    servers: dict[str, A2AServerWrapper]
) -> None:
    """Stop all A2A agent servers."""
    stop_tasks = [server.stop() for server in servers.values()]
    await asyncio.gather(*stop_tasks)
    logger.info("All A2A agent servers stopped")
