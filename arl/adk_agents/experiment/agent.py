"""Experiment designer agent."""

from typing import Any

from google.adk import Agent

from arl.adk_agents.experiment.templates import TEMPLATES
from arl.config.llm_config import POWERFUL_LLM_CONFIG
from arl.integrations.llm.provider import LLMProvider


class ExperimentDesignerAgent(Agent):
    """
    Agent for designing experimental protocols.

    Capabilities:
    - Generate experiment designs from hypotheses
    - Select appropriate templates
    - Define parameters and validation criteria
    - Estimate resource requirements
    """

    def __init__(self, name: str = "experiment_designer"):
        """Initialize experiment designer."""
        super().__init__(name=name)

    def _get_llm_provider(self) -> LLMProvider:
        """Get LLM provider instance."""
        return LLMProvider(config=POWERFUL_LLM_CONFIG)

    def _get_templates(self) -> dict:
        """Get experiment templates."""
        return TEMPLATES

    async def run(
        self,

        hypothesis: str,
        domain: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Design experimental protocol.

        Args:
            hypothesis: Research hypothesis to test
            domain: Scientific domain
            constraints: Resource or methodological constraints

        Returns:
            Experiment design with protocol and parameters
        """
        constraints = constraints or {}

        # Get templates and LLM provider
        templates = self._get_templates()
        llm_provider = self._get_llm_provider()

        # Select appropriate template
        template_description = "\n".join([
            f"- {name}: {t.description}"
            for name, t in templates.items()
        ])

        system_prompt = f"""You are an experiment design expert in {domain}.

Your task is to create detailed, reproducible experimental protocols to test research hypotheses.

Available templates:
{template_description}

Guidelines:
1. Select most appropriate template for the hypothesis
2. Define specific parameters and ranges
3. Specify validation criteria (statistical tests, significance levels)
4. Include control conditions and baselines
5. Consider resource constraints
6. Ensure reproducibility"""

        user_prompt = f"""Design an experiment to test this hypothesis:

HYPOTHESIS:
{hypothesis}

DOMAIN: {domain}

CONSTRAINTS:
{constraints}

Provide a detailed experimental protocol including:
1. Selected template and justification
2. Specific experimental methods
3. Parameters and their ranges/values
4. Statistical validation criteria (p-values, confidence intervals)
5. Control conditions
6. Expected outcomes
7. Resource estimation (time, compute, memory)

Format as structured JSON."""

        # Generate experiment design
        response = llm_provider.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        design = {
            "hypothesis": hypothesis,
            "domain": domain,
            "protocol": response.content,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
        }

        return design


def create_experiment_designer() -> ExperimentDesignerAgent:
    """Factory function for experiment designer."""
    return ExperimentDesignerAgent()
