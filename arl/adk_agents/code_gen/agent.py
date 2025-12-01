"""Code generation agent using ADK."""

from typing import Any

from google.adk import Agent

from arl.adk_agents.code_gen.validator import CodeValidator
from arl.config.llm_config import POWERFUL_LLM_CONFIG
from arl.integrations.llm.provider import LLMProvider


class CodeGeneratorAgent(Agent):
    """
    Agent for generating Python experiment code.

    Capabilities:
    - Generate production-ready Python code
    - Follow best practices (type hints, documentation)
    - Validate code safety before execution
    - Modular code structure
    """

    def __init__(self, name: str = "code_generator"):
        """Initialize code generator."""
        super().__init__(name=name)

    def _get_llm_provider(self) -> LLMProvider:
        """Get LLM provider instance."""
        return LLMProvider(config=POWERFUL_LLM_CONFIG)

    def _get_validator(self) -> CodeValidator:
        """Get code validator instance."""
        return CodeValidator()

    async def run(
        self,

        experiment_design: dict[str, Any],
        domain: str,
    ) -> dict[str, Any]:
        """
        Generate experiment code.

        Args:
            experiment_design: Experiment design specification
            domain: Scientific domain

        Returns:
            Generated code with validation results
        """
        system_prompt = """You are an expert Python developer specializing in scientific computing.

Your task is to generate production-ready, well-documented Python code for research experiments.

Requirements:
1. Use scientific Python stack (numpy, scipy, pandas, matplotlib, scikit-learn)
2. Modular structure with separate functions
3. Type hints for all functions
4. Comprehensive docstrings
5. Inline comments for complex logic
6. Error handling
7. Clear variable names
8. **CRITICAL: Generate synthetic data using sklearn.datasets or numpy.random**
9. **DO NOT load external CSV files or datasets from disk**
10. **NO network access - all data must be generated in code**
11. Save results/plots to /workspace (e.g., results.csv, plot.png)

Code structure:
- Synthetic data generation functions (use make_classification, make_regression, etc.)
- Processing/analysis functions
- Visualization functions
- Main execution function
- if __name__ == "__main__" block

Example data generation:
```python
from sklearn.datasets import make_classification
X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
```"""

        user_prompt = f"""Generate Python code for this experiment:

EXPERIMENT DESIGN:
{experiment_design}

DOMAIN: {domain}

Generate complete, executable Python code that:
1. Implements the experimental protocol exactly
2. Follows the specified methods and parameters
3. Produces the required outputs and visualizations
4. Includes statistical validation
5. Is fully self-contained and reproducible

Return ONLY the Python code, no explanations."""

        # Get instances
        llm_provider = self._get_llm_provider()
        validator = self._get_validator()

        # Generate code
        response = llm_provider.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        # Extract code (remove markdown formatting if present)
        code = response.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()

        # Validate code
        validation = validator.validate_python(code)

        # Extract dependencies
        dependencies = validator.check_dependencies(code)

        result = {
            "code": code,
            "validation": validation.dict(),
            "dependencies": dependencies,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
        }

        return result


def create_code_generator() -> CodeGeneratorAgent:
    """Factory function for code generator."""
    return CodeGeneratorAgent()
