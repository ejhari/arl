"""Analysis and validation agent."""

from typing import Any

from google.adk import Agent

from arl.config.llm_config import POWERFUL_LLM_CONFIG
from arl.integrations.llm.provider import LLMProvider


class AnalysisAgent(Agent):
    """
    Agent for analyzing experiment results.

    Capabilities:
    - Statistical analysis of results
    - Hypothesis validation (support/refute)
    - Identify limitations and caveats
    - Suggest next steps
    """

    def __init__(self, name: str = "analysis_agent"):
        """Initialize analysis agent."""
        super().__init__(name=name)

    def _get_llm_provider(self) -> LLMProvider:
        """Get LLM provider instance."""
        return LLMProvider(config=POWERFUL_LLM_CONFIG)

    async def run(
        self,

        hypothesis: str,
        experiment_design: dict[str, Any],
        execution_results: dict[str, Any],
        domain: str,
    ) -> dict[str, Any]:
        """
        Analyze experiment results.

        Args:
            hypothesis: Original hypothesis
            experiment_design: Experiment design specification
            execution_results: Execution outputs and artifacts
            domain: Scientific domain

        Returns:
            Analysis with validation outcome and recommendations
        """
        system_prompt = f"""You are a scientific analysis expert in {domain}.

Your task is to rigorously analyze experimental results and validate hypotheses.

Guidelines:
1. Perform statistical significance testing
2. Calculate effect sizes
3. Compare to baselines and controls
4. Assess whether results support or refute hypothesis
5. Identify limitations and caveats
6. Suggest refinements or next experiments
7. Be critical and objective"""

        user_prompt = f"""Analyze these experimental results:

HYPOTHESIS:
{hypothesis}

EXPERIMENT DESIGN:
{experiment_design}

EXECUTION RESULTS:
- Success: {execution_results.get('success')}
- Output: {execution_results.get('stdout', '')[:1000]}
- Artifacts: {execution_results.get('artifacts', [])}

Provide comprehensive analysis including:
1. Statistical significance assessment
2. Effect size and practical significance
3. Comparison to baselines
4. Hypothesis outcome: SUPPORTED / REFUTED / INCONCLUSIVE
5. Confidence level (0-1)
6. Evidence summary (what results led to this conclusion)
7. Limitations and caveats
8. Alternative explanations
9. Recommended next steps

Format as structured JSON."""

        # Get LLM provider instance
        llm_provider = self._get_llm_provider()

        # Generate analysis
        response = llm_provider.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        analysis = {
            "hypothesis": hypothesis,
            "raw_analysis": response.content,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
        }

        return analysis


def create_analysis_agent() -> AnalysisAgent:
    """Factory function for analysis agent."""
    return AnalysisAgent()
