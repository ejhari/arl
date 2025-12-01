"""Main orchestration agent for research workflows."""

from typing import Any

from google.adk import Agent

from arl.adk_agents.analysis.agent import create_analysis_agent
from arl.adk_agents.code_gen.agent import create_code_generator
from arl.adk_agents.execution.agent import create_execution_engine
from arl.adk_agents.experiment.agent import create_experiment_designer
from arl.adk_agents.hypothesis.agent import create_hypothesis_agent
from arl.config.llm_config import POWERFUL_LLM_CONFIG
from arl.core.memory import MemoryService
from arl.core.session import SessionService
from arl.integrations.llm.provider import LLMProvider


class OrchestratorAgent(Agent):
    """
    Main orchestration agent for research workflows.

    Responsibilities:
    - Route tasks to specialist agents
    - Manage workflow state
    - Coordinate human interaction checkpoints
    - Handle errors and recovery
    """

    def __init__(self, name: str = "orchestrator"):
        """Initialize orchestrator."""
        super().__init__(name=name, model=POWERFUL_LLM_CONFIG.model)

        # Initialize specialist agents (lazy loaded to avoid circular imports)
        self._hypothesis_agent = None
        self._experiment_designer = None
        self._code_generator = None
        self._execution_engine = None
        self._analysis_agent = None

        # Services
        self._session_service = None
        self._memory_service = None

    @property
    def hypothesis_agent(self):
        if self._hypothesis_agent is None:
            self._hypothesis_agent = create_hypothesis_agent()
        return self._hypothesis_agent

    @property
    def experiment_designer(self):
        if self._experiment_designer is None:
            self._experiment_designer = create_experiment_designer()
        return self._experiment_designer

    @property
    def code_generator(self):
        if self._code_generator is None:
            self._code_generator = create_code_generator()
        return self._code_generator

    @property
    def execution_engine(self):
        if self._execution_engine is None:
            self._execution_engine = create_execution_engine()
        return self._execution_engine

    @property
    def analysis_agent(self):
        if self._analysis_agent is None:
            self._analysis_agent = create_analysis_agent()
        return self._analysis_agent

    @property
    def session_service(self):
        if self._session_service is None:
            self._session_service = SessionService()
        return self._session_service

    @property
    def memory_service(self):
        if self._memory_service is None:
            self._memory_service = MemoryService()
        return self._memory_service

    async def run(
        self,
        
        session_id: str,
        user_request: str,
    ) -> dict[str, Any]:
        """
        Process user request and orchestrate workflow.

        Args:
            session_id: Active session ID
            user_request: User's research request

        Returns:
            Workflow results
        """
        # Load session state
        session = self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Determine workflow stage from user request and session state
        workflow_stage = await self._determine_stage(user_request, session.state or {})

        # Execute appropriate workflow
        if workflow_stage == "hypothesis_generation":
            result = await self._hypothesis_workflow(session_id, user_request)
        elif workflow_stage == "experiment_design":
            result = await self._experiment_workflow(session_id, user_request)
        elif workflow_stage == "execution":
            result = await self._execution_workflow(session_id, user_request)
        else:
            result = {"error": f"Unknown workflow stage: {workflow_stage}"}

        # Update session state
        self.session_service.update_state(session_id, result)

        return result

    async def _determine_stage(
        self,
        user_request: str,
        session_state: dict[str, Any],
    ) -> str:
        """Determine current workflow stage."""
        # Simplified stage detection for v1.0
        # In production, would use LLM classification

        if "hypotheses" not in session_state:
            return "hypothesis_generation"
        elif "design" not in session_state:
            return "experiment_design"
        elif "execution" not in session_state:
            return "execution"
        else:
            return "analysis"

    async def _hypothesis_workflow(
        self,
        
        session_id: str,
        user_request: str,
    ) -> dict[str, Any]:
        """Execute hypothesis generation workflow."""
        # Extract literature summary from request (simplified)
        literature_summary = user_request
        research_gap = "To be identified"  # Would extract from literature analysis

        # Generate hypotheses
        hypotheses = await self.hypothesis_agent.run(
            
            literature_summary=literature_summary,
            research_gap=research_gap,
            domain="general",
        )

        # Store in memory
        self.memory_service.store_memory(
            session_id=session_id,
            key="hypotheses",
            value=hypotheses,
        )

        return {"stage": "hypothesis_generation", "hypotheses": hypotheses}

    async def _experiment_workflow(
        self,

        session_id: str,
        user_request: str,
    ) -> dict[str, Any]:
        """Execute experiment design workflow."""
        # Retrieve hypothesis from session state
        session = self.session_service.get_session(session_id)
        hypotheses = session.state.get("hypotheses", {})
        hypothesis = hypotheses.get("raw_output", "")  # Simplified

        # Design experiment
        design = await self.experiment_designer.run(
            
            hypothesis=hypothesis,
            domain="general",
        )

        # Generate code
        code_result = await self.code_generator.run(
            
            experiment_design=design,
            domain="general",
        )

        # Store in memory
        self.memory_service.store_memory(session_id, "experiment_design", design)
        self.memory_service.store_memory(session_id, "generated_code", code_result)

        return {
            "stage": "experiment_design",
            "design": design,
            "code": code_result,
        }

    async def _execution_workflow(
        self,

        session_id: str,
        user_request: str,
    ) -> dict[str, Any]:
        """Execute experiment execution workflow."""
        # Retrieve code from session state
        session = self.session_service.get_session(session_id)
        code_result = session.state.get("code", {})
        code = code_result.get("code", "")

        # Check if Docker is available and working
        try:
            # Test Docker availability before trying to execute
            import docker
            docker_client = docker.from_env()
            docker_client.ping()
            docker_available = True
        except Exception as e:
            docker_available = False
            docker_error = str(e)

        if not docker_available:
            # Docker not available - return simulated results
            execution_result = {
                "success": False,
                "stdout": "",
                "stderr": f"Docker not available: {docker_error}\n\nExecution skipped. Please ensure Docker is running and try again.",
                "exit_code": -1,
                "artifacts": [],
                "experiment_id": f"exp_{session_id}",
                "skipped": True,
            }

            # Still analyze with simulated results
            hypotheses = session.state.get("hypotheses", {})
            design = session.state.get("design", {})

            analysis = await self.analysis_agent.run(
                hypothesis=hypotheses.get("raw_output", ""),
                experiment_design=design,
                execution_results=execution_result,
                domain="general",
            )

            return {
                "stage": "execution_complete",
                "execution": execution_result,
                "analysis": analysis,
                "docker_available": False,
            }

        # Docker is available - execute experiment
        try:
            execution_result = await self.execution_engine.run(
                experiment_id=f"exp_{session_id}",
                code=code,
            )
        except Exception as e:
            # Execution failed
            execution_result = {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": -1,
                "artifacts": [],
                "experiment_id": f"exp_{session_id}",
                "skipped": False,
            }

        # Analyze results
        hypotheses = session.state.get("hypotheses", {})
        design = session.state.get("design", {})

        analysis = await self.analysis_agent.run(

            hypothesis=hypotheses.get("raw_output", ""),
            experiment_design=design,
            execution_results=execution_result,
            domain="general",
        )

        # Store results
        self.memory_service.store_memory(session_id, "execution_result", execution_result)
        self.memory_service.store_memory(session_id, "analysis", analysis)

        return {
            "stage": "execution_complete",
            "execution": execution_result,
            "analysis": analysis,
            "docker_available": True,
        }


def create_orchestrator() -> OrchestratorAgent:
    """Factory function for orchestrator."""
    return OrchestratorAgent()
