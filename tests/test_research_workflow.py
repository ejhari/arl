"""End-to-end tests for complete research workflow."""

import asyncio
from pathlib import Path

import pytest

from arl.adk_agents.analysis.agent import create_analysis_agent
from arl.adk_agents.code_gen.agent import create_code_generator
from arl.adk_agents.execution.agent import create_execution_engine
from arl.adk_agents.experiment.agent import create_experiment_designer
from arl.adk_agents.hypothesis.agent import create_hypothesis_agent
from arl.adk_agents.orchestrator.agent import create_orchestrator
from arl.config.settings import settings
from arl.core.knowledge.paper_service import PaperService
from arl.core.memory.memory_service import MemoryService
from arl.core.project.project_service import ProjectService
from arl.core.session.session_service import SessionService
from arl.integrations.papers.arxiv_client import ArxivClient
from arl.integrations.papers.pdf_parser import PDFParser
from arl.storage.database import init_db
from arl.storage.models import DomainType, SessionStatus


class TestDatabaseSetup:
    """Test database initialization."""

    def test_init_db(self):
        """Test database initialization."""
        init_db()
        assert settings.data_dir.exists()


class TestProjectManagement:
    """Test project management workflow."""

    def test_create_project(self):
        """Test project creation."""
        service = ProjectService()
        project = service.create_project(
            name="Test Project",
            domain=DomainType.CS,
            objectives="Test objectives",
        )

        assert project.project_id is not None
        assert project.name == "Test Project"
        assert project.domain == DomainType.CS

    def test_list_projects(self):
        """Test listing projects."""
        service = ProjectService()
        projects = service.list_projects()
        assert isinstance(projects, list)

    def test_get_project(self):
        """Test getting specific project."""
        service = ProjectService()
        project = service.create_project("Test Get", DomainType.CS)
        retrieved = service.get_project(project.project_id)

        assert retrieved is not None
        assert retrieved.project_id == project.project_id


class TestSessionManagement:
    """Test session management workflow."""

    def test_create_session(self):
        """Test session creation."""
        project_service = ProjectService()
        project = project_service.create_project("Session Test", DomainType.CS)

        session_service = SessionService()
        session = session_service.create_session(project.project_id)

        assert session.session_id is not None
        assert session.project_id == project.project_id
        assert session.status == SessionStatus.ACTIVE

    def test_update_session_state(self):
        """Test session state updates."""
        project_service = ProjectService()
        project = project_service.create_project("State Test", DomainType.CS)

        session_service = SessionService()
        session = session_service.create_session(project.project_id)

        state = {"test_key": "test_value", "stage": "hypothesis"}
        updated = session_service.update_state(session.session_id, state)

        assert updated.state == state

    def test_add_event(self):
        """Test adding events to session."""
        project_service = ProjectService()
        project = project_service.create_project("Event Test", DomainType.CS)

        session_service = SessionService()
        session = session_service.create_session(project.project_id)

        event = {"type": "hypothesis_generated", "data": "test"}
        updated = session_service.add_event(session.session_id, event)

        assert len(updated.events) > 0
        assert updated.events[0]["type"] == "hypothesis_generated"


class TestMemoryService:
    """Test memory service."""

    def test_store_and_retrieve(self):
        """Test storing and retrieving memory."""
        service = MemoryService()
        session_id = "test_session_123"

        service.store_memory(session_id, "test_key", {"data": "test_value"})
        retrieved = service.retrieve_memory(session_id, "test_key")

        assert retrieved == {"data": "test_value"}

    def test_list_memories(self):
        """Test listing all memories."""
        service = MemoryService()
        session_id = "test_session_456"

        service.store_memory(session_id, "key1", "value1")
        service.store_memory(session_id, "key2", "value2")

        memories = service.list_memories(session_id)

        assert "key1" in memories
        assert "key2" in memories


class TestCodeValidation:
    """Test code generation and validation."""

    def test_code_validator_valid_code(self):
        """Test validation of valid code."""
        from arl.adk_agents.code_gen.validator import CodeValidator

        validator = CodeValidator()
        code = """
def hello_world() -> str:
    \"\"\"Say hello.\"\"\"
    return "Hello, World!"
"""
        result = validator.validate_python(code)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_code_validator_syntax_error(self):
        """Test validation of invalid syntax."""
        from arl.adk_agents.code_gen.validator import CodeValidator

        validator = CodeValidator()
        code = "def invalid syntax here"
        result = validator.validate_python(code)

        assert result.valid is False
        assert len(result.errors) > 0

    def test_code_validator_dangerous_patterns(self):
        """Test detection of dangerous patterns."""
        from arl.adk_agents.code_gen.validator import CodeValidator

        validator = CodeValidator()
        code = """
import os
os.system("rm -rf /")
"""
        result = validator.validate_python(code)

        assert result.valid is False
        assert any("Dangerous pattern" in err for err in result.errors)

    def test_dependency_extraction(self):
        """Test dependency extraction from code."""
        from arl.adk_agents.code_gen.validator import CodeValidator

        validator = CodeValidator()
        code = """
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
"""
        deps = validator.check_dependencies(code)

        assert "numpy" in deps
        assert "pandas" in deps
        assert "sklearn" in deps


@pytest.mark.asyncio
class TestAgentWorkflow:
    """Test individual agents."""

    async def test_hypothesis_agent(self):
        """Test hypothesis generation agent."""
        agent = create_hypothesis_agent()

        class MockContext:
            pass

        result = await agent.run(
            ctx=MockContext(),
            literature_summary="Neural networks struggle with out-of-distribution data.",
            research_gap="Limited comparison of robustness techniques.",
            domain="cs",
        )

        assert "raw_output" in result
        assert "model_used" in result
        assert "tokens_used" in result

    async def test_experiment_designer_agent(self):
        """Test experiment designer agent."""
        agent = create_experiment_designer()

        class MockContext:
            pass

        result = await agent.run(
            ctx=MockContext(),
            hypothesis="Algorithm A outperforms Algorithm B",
            domain="cs",
        )

        assert "protocol" in result
        assert "hypothesis" in result

    async def test_code_generator_agent(self):
        """Test code generator agent."""
        agent = create_code_generator()

        class MockContext:
            pass

        experiment_design = {
            "hypothesis": "Linear regression outperforms baseline",
            "methods": "Scikit-learn LinearRegression",
            "validation": "R² score, RMSE",
        }

        result = await agent.run(
            ctx=MockContext(),
            experiment_design=experiment_design,
            domain="cs",
        )

        assert "code" in result
        assert "validation" in result
        assert len(result["code"]) > 0

    async def test_analysis_agent(self):
        """Test analysis agent."""
        agent = create_analysis_agent()

        class MockContext:
            pass

        result = await agent.run(
            ctx=MockContext(),
            hypothesis="Method A outperforms Method B",
            experiment_design={"methods": ["A", "B"]},
            execution_results={
                "success": True,
                "stdout": "Method A: 0.95, Method B: 0.87",
                "artifacts": [],
            },
            domain="cs",
        )

        assert "raw_analysis" in result
        assert "hypothesis" in result


@pytest.mark.asyncio
class TestCompleteResearchWorkflow:
    """Test complete end-to-end research workflow."""

    async def test_full_workflow_three_stages(self):
        """Test complete workflow through all three stages."""
        # Setup
        project_service = ProjectService()
        project = project_service.create_project("E2E Test", DomainType.CS)

        session_service = SessionService()
        session = session_service.create_session(project.project_id)

        orchestrator = create_orchestrator()

        class MockContext:
            pass

        # Stage 1: Hypothesis Generation
        result1 = await orchestrator.run(
            ctx=MockContext(),
            session_id=session.session_id,
            user_request="Generate hypotheses about neural network robustness",
        )

        assert result1["stage"] == "hypothesis_generation"
        assert "hypotheses" in result1

        # Stage 2: Experiment Design
        result2 = await orchestrator.run(
            ctx=MockContext(),
            session_id=session.session_id,
            user_request="continue",
        )

        assert result2["stage"] == "experiment_design"
        assert "design" in result2
        assert "code" in result2

        # Stage 3: Execution & Analysis
        # Note: This would actually execute code in Docker, so we'll skip in test
        # In real test with Docker running, uncomment:
        # result3 = await orchestrator.run(
        #     ctx=MockContext(),
        #     session_id=session.session_id,
        #     user_request="continue",
        # )
        #
        # assert result3["stage"] == "execution_complete"
        # assert "execution" in result3
        # assert "analysis" in result3


class TestExperimentTemplates:
    """Test experiment templates."""

    def test_ml_comparison_template(self):
        """Test ML comparison template."""
        from arl.adk_agents.experiment.templates import ML_EXPERIMENT_TEMPLATE

        assert ML_EXPERIMENT_TEMPLATE.name == "ml_comparison"
        assert ML_EXPERIMENT_TEMPLATE.domain == "cs"
        assert "algorithms" in ML_EXPERIMENT_TEMPLATE.required_parameters

    def test_simulation_template(self):
        """Test simulation template."""
        from arl.adk_agents.experiment.templates import SIMULATION_TEMPLATE

        assert SIMULATION_TEMPLATE.name == "computational_simulation"
        assert "simulation_model" in SIMULATION_TEMPLATE.required_parameters

    def test_get_template(self):
        """Test template retrieval."""
        from arl.adk_agents.experiment.templates import get_template

        template = get_template("ml_comparison")
        assert template is not None
        assert template.name == "ml_comparison"


def test_integration_workflow():
    """Test integration between multiple services."""
    # Create project
    project_service = ProjectService()
    project = project_service.create_project("Integration Test", DomainType.CS)

    # Create session
    session_service = SessionService()
    session = session_service.create_session(project.project_id)

    # Store memory
    memory_service = MemoryService()
    memory_service.store_memory(
        session.session_id,
        "test_data",
        {"key": "value"},
    )

    # Retrieve and verify
    retrieved = memory_service.retrieve_memory(session.session_id, "test_data")
    assert retrieved == {"key": "value"}

    # Update session state
    session_service.update_state(
        session.session_id,
        {"stage": "complete", "data": retrieved},
    )

    # Verify session
    updated_session = session_service.get_session(session.session_id)
    assert updated_session.state["stage"] == "complete"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
