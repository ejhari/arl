"""A2A Agent Client - Google ADK powered agent communication

Uses Google ADK for A2A protocol compliant agents with native multi-model support:
- Anthropic Claude (native)
- Google Gemini (native)
- Azure OpenAI, AWS Bedrock, OpenAI (via ADK's built-in LiteLLM)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class A2AAgentClient:
    """
    A2A Protocol Agent Client powered by Google ADK.

    Uses Google ADK's native multi-model support for agent responses,
    falls back to stub responses when LLM is not configured.
    """

    def __init__(self, agent_name: str, service_url: Optional[str] = None):
        self.agent_name = agent_name
        self.service_url = service_url
        self.is_initialized = False
        self._adk_service = None
        self._use_adk = False

    async def initialize(self) -> None:
        """Initialize the client with Google ADK."""
        logger.info(f"Initializing A2A client for agent: {self.agent_name}")

        try:
            from app.services.adk_agents import adk_agent_service
            adk_agent_service.initialize()

            if adk_agent_service.get_agent(self.agent_name):
                self._adk_service = adk_agent_service
                self._use_adk = adk_agent_service.is_configured()
                if self._use_adk:
                    logger.info(f"ADK agent initialized for {self.agent_name}")
                else:
                    logger.warning(f"ADK not configured (no API key), using stub for {self.agent_name}")
            else:
                logger.warning(f"ADK agent {self.agent_name} not found, using stub responses")
        except Exception as e:
            logger.warning(f"Could not initialize ADK service: {e}, using stub responses")
            self._use_adk = False

        self.is_initialized = True

    async def call_skill(self, skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an agent skill.

        Uses Google ADK if configured, otherwise returns stub responses.
        """
        logger.info(f"Agent {self.agent_name} executing skill: {skill_name}")

        # Use Google ADK if configured
        if self._use_adk and self._adk_service:
            try:
                result = await self._adk_service.call_agent(
                    agent_name=self.agent_name,
                    skill_name=skill_name,
                    input_data=input_data,
                )
                logger.info(f"ADK response received for {self.agent_name}/{skill_name}")
                return result
            except Exception as e:
                logger.error(f"ADK call failed, falling back to stub: {e}")

        # Stub responses for development/testing
        return self._get_stub_response(skill_name, input_data)

    def _get_stub_response(self, skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return simulated responses for development/testing."""
        if skill_name == "generate_hypotheses":
            return {
                "status": "success",
                "raw_output": f"# Generated Hypotheses (Stub)\n\nBased on the research prompt:\n\n1. **Hypothesis 1**: Initial hypothesis based on literature\n2. **Hypothesis 2**: Alternative explanation\n3. **Hypothesis 3**: Novel approach hypothesis\n\nInput: {input_data.get('literature_summary', 'N/A')}\n\n*Note: Configure ANTHROPIC_API_KEY or GOOGLE_API_KEY for real LLM responses.*",
                "hypotheses": [
                    {"id": "h1", "text": "Primary hypothesis", "confidence": 0.8},
                    {"id": "h2", "text": "Secondary hypothesis", "confidence": 0.6},
                ],
            }

        elif skill_name == "design_experiment":
            return {
                "status": "success",
                "raw_output": "# Experiment Design (Stub)\n\n## Methodology\n- Step 1: Setup\n- Step 2: Execute\n- Step 3: Collect data\n\n## Expected Outcomes\n- Measurement criteria defined\n- Control variables established\n\n*Note: Configure an API key for real LLM responses.*",
                "design": {
                    "steps": ["setup", "execute", "collect"],
                    "variables": ["independent", "dependent", "control"],
                },
            }

        elif skill_name == "generate_code":
            return {
                "status": "success",
                "code": """# Generated Experiment Code (Stub)

import numpy as np
import pandas as pd

def run_experiment():
    \"\"\"Execute the designed experiment.\"\"\"
    np.random.seed(42)
    data = np.random.randn(100)
    return pd.DataFrame({'results': data})

if __name__ == '__main__':
    results = run_experiment()
    print(results.describe())

# Note: Configure an API key for real LLM responses.
""",
                "language": "python",
            }

        elif skill_name == "execute_experiment":
            return {
                "status": "success",
                "raw_output": "# Experiment Execution Results (Stub)\n\nExperiment completed successfully.\n\n## Results Summary\n- Samples processed: 100\n- Success rate: 95%\n- Execution time: 2.3s\n\n*Note: Configure an API key for real LLM responses.*",
                "execution_id": input_data.get("experiment_id", "unknown"),
                "metrics": {
                    "samples": 100,
                    "success_rate": 0.95,
                    "duration": 2.3,
                },
            }

        elif skill_name == "analyze_results":
            return {
                "status": "success",
                "raw_output": "# Analysis Report (Stub)\n\n## Statistical Analysis\n- Mean: 0.05\n- Std Dev: 1.02\n- P-value: 0.03\n\n## Conclusions\nThe results support the primary hypothesis with statistical significance (p < 0.05).\n\n## Recommendations\n1. Further investigation recommended\n2. Consider expanding sample size\n\n*Note: Configure an API key for real LLM responses.*",
                "analysis": {
                    "hypothesis_supported": True,
                    "confidence": 0.85,
                    "p_value": 0.03,
                },
            }

        else:
            return {
                "status": "success",
                "raw_output": f"# Agent Output (Stub)\n\nAgent: {self.agent_name}\nSkill: {skill_name}\n\nExecution completed.\n\n*Note: Configure an API key for real LLM responses.*",
                "input_received": input_data,
            }

    async def get_agent_card(self) -> Dict[str, Any]:
        """Get the agent's A2A protocol card."""
        return {
            "name": self.agent_name,
            "version": "1.0.0",
            "protocol_version": "0.3",
            "capabilities": ["research", "analysis"],
            "adk_enabled": self._use_adk,
        }

    async def close(self) -> None:
        """Close the client connection."""
        logger.info(f"Closing A2A client for agent: {self.agent_name}")
        self.is_initialized = False
