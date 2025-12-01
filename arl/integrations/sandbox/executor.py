"""Docker-based code execution sandbox."""

import shutil
import tempfile
from pathlib import Path
from typing import Any

import docker
from docker.errors import DockerException
from pydantic import BaseModel

from arl.config.settings import settings


class ExecutionResult(BaseModel):
    """Result of code execution."""

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    artifacts: list[Path] = []


class SandboxExecutor:
    """Execute code in isolated Docker container."""

    def __init__(self):
        """Initialize Docker client."""
        if not settings.docker_enabled:
            raise RuntimeError("Docker is not enabled in settings")

        try:
            self.client = docker.from_env()
            self.client.ping()
        except DockerException as e:
            raise RuntimeError(f"Docker not available: {e}")

        # Build or pull sandbox image
        self._ensure_sandbox_image()

    def _ensure_sandbox_image(self) -> None:
        """Ensure sandbox Docker image exists."""
        image_name = "arl-sandbox:latest"
        try:
            self.client.images.get(image_name)
        except docker.errors.ImageNotFound:
            # Build from Dockerfile
            dockerfile_path = Path(__file__).parent / "Dockerfile.sandbox"
            if dockerfile_path.exists():
                self.client.images.build(
                    path=str(dockerfile_path.parent),
                    dockerfile=str(dockerfile_path.name),
                    tag=image_name,
                )

    def _create_wrapper_script(self, dependencies: list[str]) -> str:
        """
        Create bash wrapper script that installs dependencies then runs experiment.

        Args:
            dependencies: List of package requirements

        Returns:
            Bash script content
        """
        deps_str = " ".join(f'"{dep}"' for dep in dependencies)

        return f"""#!/bin/bash
set -e

echo "Installing dynamic dependencies with uv..."
echo "Dependencies: {deps_str}"
echo ""

# Install dependencies using uv (fast!)
uv pip install --system {deps_str}

echo ""
echo "Dependencies installed. Running experiment..."
echo "================================================"
echo ""

# Run the experiment
python /workspace/experiment.py
"""

    def execute_code(
        self,
        code: str,
        dependencies: list[str] | None = None,
        timeout_seconds: int | None = None,
        working_dir: Path | None = None,
    ) -> ExecutionResult:
        """
        Execute Python code in sandbox with optional dynamic dependencies.

        Args:
            code: Python code to execute
            dependencies: Optional list of package requirements to install dynamically
                         (e.g., ["requests>=2.28.0", "beautifulsoup4"])
            timeout_seconds: Execution timeout (default: from settings)
            working_dir: Working directory with input files

        Returns:
            ExecutionResult with stdout, stderr, and artifacts
        """
        timeout = timeout_seconds or settings.experiment_timeout_seconds

        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write code to file
            code_file = tmp_path / "experiment.py"
            code_file.write_text(code)

            # Copy working directory files if provided
            if working_dir and working_dir.exists():
                for item in working_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, tmp_path / item.name)

            # Create execution command
            if dependencies:
                # Create wrapper script that installs dependencies then runs code
                wrapper_script = self._create_wrapper_script(dependencies)
                wrapper_file = tmp_path / "run_experiment.sh"
                wrapper_file.write_text(wrapper_script)
                wrapper_file.chmod(0o755)
                command = ["/bin/bash", "/workspace/run_experiment.sh"]
                # Enable network for dependency installation
                network_mode = "bridge"
            else:
                # Direct execution without dependency installation
                command = ["python", "/workspace/experiment.py"]
                network_mode = "none"

            # Setup volumes
            volumes = {str(tmp_path): {"bind": "/workspace", "mode": "rw"}}

            # Add shared uv cache volume for faster installs
            uv_cache_dir = (settings.data_dir / "uv_cache").resolve().absolute()
            uv_cache_dir.mkdir(parents=True, exist_ok=True)
            volumes[str(uv_cache_dir)] = {"bind": "/home/researcher/.cache/uv", "mode": "rw"}

            # Run container
            try:
                container = self.client.containers.run(
                    image="arl-sandbox:latest",
                    command=command,
                    volumes=volumes,
                    working_dir="/workspace",
                    network_mode=network_mode,
                    mem_limit="2g",
                    cpu_quota=100000,  # 1 CPU
                    detach=True,
                    remove=False,
                )

                # Wait for completion
                result = container.wait(timeout=timeout)
                logs = container.logs(stdout=True, stderr=True).decode("utf-8")

                # Separate stdout and stderr (simplified)
                stdout = logs
                stderr = ""
                exit_code = result["StatusCode"]

                # Collect artifacts
                artifacts = []
                for item in tmp_path.iterdir():
                    if item.name != "experiment.py":
                        artifacts.append(item)

                # Clean up container
                container.remove()

                return ExecutionResult(
                    success=(exit_code == 0),
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    artifacts=artifacts,
                )

            except Exception as e:
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution error: {str(e)}",
                    exit_code=-1,
                )
