"""Execution engine agent."""

import shutil
from pathlib import Path
from typing import Any

from google.adk import Agent
from pydantic import PrivateAttr

from arl.config.settings import settings
from arl.integrations.sandbox.executor import ExecutionResult, SandboxExecutor
from arl.storage.models import Experiment, ExperimentStatus


class ExecutionEngineAgent(Agent):
    """
    Agent for executing experiments in sandbox.

    Capabilities:
    - Execute code in isolated Docker container
    - Monitor execution and capture output
    - Collect result artifacts
    - Handle errors and timeouts
    """

    _executor: SandboxExecutor = PrivateAttr()

    def __init__(self, name: str = "execution_engine"):
        """Initialize execution engine."""
        super().__init__(name=name)
        self._executor = SandboxExecutor()

    async def run(
        self,
        experiment_id: str,
        code: str,
        dependencies: list[str] | None = None,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute experiment code with optional dynamic dependencies.

        Args:
            experiment_id: Experiment ID for artifact storage
            code: Python code to execute
            dependencies: Optional list of package requirements to install dynamically
            timeout_seconds: Execution timeout

        Returns:
            Execution results with outputs and artifacts
        """
        # Create experiment directory for artifacts
        exp_dir = settings.artifacts_dir / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)

        # Execute in sandbox with dynamic dependencies
        result: ExecutionResult = self._executor.execute_code(
            code=code,
            dependencies=dependencies,
            timeout_seconds=timeout_seconds,
        )

        # Copy artifacts to permanent storage
        artifact_paths = []
        for artifact in result.artifacts:
            dest = exp_dir / artifact.name
            if artifact.is_file():
                shutil.copy2(artifact, dest)
                artifact_paths.append(str(dest))
            elif artifact.is_dir():
                shutil.copytree(artifact, dest, dirs_exist_ok=True)
                artifact_paths.append(str(dest))

        # Structure results
        execution_result = {
            "success": result.success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "artifacts": artifact_paths,
            "experiment_id": experiment_id,
        }

        return execution_result


def create_execution_engine() -> ExecutionEngineAgent:
    """Factory function for execution engine."""
    return ExecutionEngineAgent()
