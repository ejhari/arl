"""Hypothesis generation agent using ADK."""

from typing import Any

from google.genai import types
from google.adk import Agent

from arl.config.llm_config import POWERFUL_LLM_CONFIG
from arl.integrations.llm.provider import LLMProvider


class HypothesisAgent(Agent):
    """
    Agent for generating testable research hypotheses.

    Capabilities:
    - Generate hypotheses from literature analysis
    - Assess testability and novelty
    - Rank hypotheses by feasibility and impact
    """

    def __init__(self, name: str = "hypothesis_agent"):
        """Initialize hypothesis agent."""
        super().__init__(name=name, model=POWERFUL_LLM_CONFIG.model)

    def _get_llm_provider(self) -> LLMProvider:
        """Get LLM provider instance."""
        return LLMProvider(config=POWERFUL_LLM_CONFIG)

    async def run(
        self,
        literature_summary: str,
        research_gap: str,
        domain: str,
    ) -> dict[str, Any]:
        """
        Generate research hypotheses.

        Args:
            literature_summary: Summary of reviewed literature
            research_gap: Identified research gap
            domain: Scientific domain (cs, biology, etc.)

        Returns:
            Dict with hypotheses and rankings
        """
        system_prompt = f"""You are a scientific hypothesis generation expert in {domain}.

Your task is to generate testable, novel research hypotheses based on literature review and identified gaps.

Guidelines:
1. Hypotheses must be testable through computational experiments
2. Hypotheses should address the identified research gap
3. Ground hypotheses in cited literature
4. Assess feasibility for implementation
5. Evaluate novelty and potential impact"""

        user_prompt = f"""Based on the following literature review and research gap, generate 3-5 testable research hypotheses.

LITERATURE SUMMARY:
{literature_summary}

RESEARCH GAP:
{research_gap}

For each hypothesis, provide:
1. Clear hypothesis statement
2. Testability assessment (how can this be validated?)
3. Novelty score (0-1, how original is this?)
4. Feasibility score (0-1, how implementable?)
5. Literature grounding (which papers support this direction?)
6. Expected impact

Format as JSON array."""

        # Generate hypotheses
        llm_provider = self._get_llm_provider()
        response = llm_provider.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        # Parse and structure response (simplified for v1.0)
        # In production, would use structured output or JSON parsing
        hypotheses = {
            "raw_output": response.content,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
        }

        return hypotheses


# Register agent with ADK
def create_hypothesis_agent() -> HypothesisAgent:
    """Factory function for creating hypothesis agent."""
    return HypothesisAgent()
