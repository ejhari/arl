"""Domain-specific experiment templates."""

from typing import Any

from pydantic import BaseModel


class ExperimentTemplate(BaseModel):
    """Template for experiment design."""

    name: str
    domain: str
    description: str
    required_parameters: list[str]
    optional_parameters: list[str]
    validation_criteria: list[str]
    code_structure: dict[str, str]


# Machine Learning Experiment Template
ML_EXPERIMENT_TEMPLATE = ExperimentTemplate(
    name="ml_comparison",
    domain="cs",
    description="Compare machine learning algorithms",
    required_parameters=[
        "algorithms",
        "datasets",
        "metrics",
        "train_test_split",
    ],
    optional_parameters=[
        "cross_validation_folds",
        "hyperparameter_search",
        "random_seed",
    ],
    validation_criteria=[
        "statistical_significance_test",
        "effect_size_calculation",
        "baseline_comparison",
    ],
    code_structure={
        "data_loading": "Load and preprocess datasets",
        "algorithm_setup": "Initialize algorithms with parameters",
        "training": "Train models with cross-validation",
        "evaluation": "Calculate metrics and statistical tests",
        "visualization": "Generate comparison plots",
    },
)

# Computational Simulation Template
SIMULATION_TEMPLATE = ExperimentTemplate(
    name="computational_simulation",
    domain="general",
    description="Run computational simulations",
    required_parameters=[
        "simulation_model",
        "parameter_ranges",
        "iterations",
        "output_metrics",
    ],
    optional_parameters=[
        "sensitivity_analysis",
        "parallel_execution",
    ],
    validation_criteria=[
        "convergence_check",
        "stability_analysis",
        "reproducibility_test",
    ],
    code_structure={
        "model_definition": "Define simulation model",
        "parameter_setup": "Set parameter ranges",
        "simulation_loop": "Run simulation iterations",
        "data_collection": "Collect output metrics",
        "analysis": "Analyze results and trends",
    },
)


TEMPLATES = {
    "ml_comparison": ML_EXPERIMENT_TEMPLATE,
    "simulation": SIMULATION_TEMPLATE,
}


def get_template(template_name: str) -> ExperimentTemplate | None:
    """Get experiment template by name."""
    return TEMPLATES.get(template_name)
