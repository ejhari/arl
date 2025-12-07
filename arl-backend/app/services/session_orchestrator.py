"""Session Orchestrator - Coordinates multi-agent research workflows"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.session import Session, SessionAgent, SessionMemory, SessionCell
from app.models.agent import Agent
from app.models.cell import Cell
from app.services.a2a_client import A2AAgentClient
from app.core.websocket import ws_manager

logger = logging.getLogger(__name__)


class AgentTask:
    """Represents a task assigned to an agent"""

    def __init__(
        self,
        task_id: str,
        agent_id: str,
        agent_name: str,
        skill_name: str,
        input_data: Dict[str, Any],
        depends_on: Optional[List[str]] = None,
    ):
        self.task_id = task_id
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.skill_name = skill_name
        self.input_data = input_data
        self.depends_on = depends_on or []
        self.status = "pending"  # pending | running | completed | failed
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None


class SessionOrchestrator:
    """
    Orchestrates multi-agent research workflows within a session.

    Responsibilities:
    - Coordinate task execution across multiple agents
    - Manage task dependencies and execution order
    - Route tasks to appropriate agents via A2A protocol
    - Emit real-time progress events via WebSocket
    - Create cells and memories from agent outputs
    """

    def __init__(self, db: AsyncSession, session_id: str, user_id: str):
        self.db = db
        self.session_id = session_id
        self.user_id = user_id
        self.tasks: Dict[str, AgentTask] = {}
        self.agent_clients: Dict[str, A2AAgentClient] = {}
        self.session: Optional[Session] = None
        self.session_agents: List[SessionAgent] = []

    async def initialize(self) -> None:
        """Initialize orchestrator by loading session and agents"""
        # Load session
        result = await self.db.execute(
            select(Session).where(Session.id == self.session_id)
        )
        self.session = result.scalar_one_or_none()

        if not self.session:
            raise ValueError(f"Session {self.session_id} not found")

        # Load enabled session agents
        result = await self.db.execute(
            select(SessionAgent, Agent)
            .join(Agent, SessionAgent.agent_id == Agent.id)
            .where(
                SessionAgent.session_id == self.session_id,
                SessionAgent.is_enabled == True,
                Agent.is_active == True,
            )
        )
        rows = result.all()
        self.session_agents = [sa for sa, _ in rows]

        # Initialize A2A clients for each agent (stub client works without real endpoints)
        for sa, agent in rows:
            try:
                client = A2AAgentClient(
                    agent_name=agent.name,
                    service_url=agent.service_endpoint,  # Can be None for stub
                )
                await client.initialize()
                self.agent_clients[agent.id] = client
                logger.info(f"Initialized A2A client for agent {agent.name}")
            except Exception as e:
                logger.error(f"Failed to initialize A2A client for {agent.name}: {e}")

        logger.info(f"Orchestrator initialized for session {self.session_id} with {len(self.agent_clients)} agents")

    async def execute_research_workflow(self, initial_prompt: str) -> Dict[str, Any]:
        """
        Execute the full research workflow with all enabled agents.

        This is the main entry point for autonomous multi-agent research.

        Workflow:
        1. Hypothesis Agent → Generate hypotheses
        2. Experiment Designer → Design experiments for each hypothesis
        3. Code Generator → Generate experiment code
        4. Execution Engine → Run experiments
        5. Analysis Agent → Analyze results

        Args:
            initial_prompt: The research question or prompt

        Returns:
            Workflow execution summary
        """
        try:
            # Update session status
            if self.session:
                self.session.status = "active"
                await self.db.commit()

            # Emit workflow started event
            await self._emit_event("workflow_started", {
                "session_id": self.session_id,
                "prompt": initial_prompt,
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Create task plan
            tasks = await self._plan_research_tasks(initial_prompt)

            # Execute tasks in dependency order
            results = await self._execute_tasks(tasks)

            # Update session status
            if self.session:
                self.session.status = "completed"
                self.session.session_metadata = {
                    "workflow_completed_at": datetime.utcnow().isoformat(),
                    "tasks_executed": len(tasks),
                    "results_summary": self._summarize_results(results),
                }
                await self.db.commit()

            # Emit workflow completed event
            await self._emit_event("workflow_completed", {
                "session_id": self.session_id,
                "tasks_completed": len(tasks),
                "timestamp": datetime.utcnow().isoformat(),
            })

            return {
                "status": "success",
                "tasks_completed": len(tasks),
                "results": results,
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)

            # Update session to failed status
            if self.session:
                self.session.status = "failed"
                self.session.session_metadata = {
                    "error": str(e),
                    "failed_at": datetime.utcnow().isoformat(),
                }
                await self.db.commit()

            # Emit error event
            await self._emit_event("workflow_failed", {
                "session_id": self.session_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })

            raise

    async def execute_single_agent(
        self,
        agent_id: str,
        skill_name: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a single agent skill.

        Args:
            agent_id: ID of the agent to execute
            skill_name: Name of the skill to invoke
            input_data: Input parameters for the skill

        Returns:
            Agent execution result
        """
        # Get agent client
        client = self.agent_clients.get(agent_id)
        if not client:
            raise ValueError(f"Agent {agent_id} not available")

        # Get agent details
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Emit agent started event
        await self._emit_event("agent_started", {
            "session_id": self.session_id,
            "agent_id": agent_id,
            "agent_name": agent.name,
            "agent_display_name": agent.display_name,
            "skill_name": skill_name,
            "timestamp": datetime.utcnow().isoformat(),
        })

        try:
            # Call agent skill
            result = await client.call_skill(skill_name, input_data)

            # Emit agent completed event
            await self._emit_event("agent_completed", {
                "session_id": self.session_id,
                "agent_id": agent_id,
                "agent_name": agent.name,
                "skill_name": skill_name,
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Create cell from result if applicable
            await self._create_cell_from_result(agent, skill_name, result)

            # Create memory from result
            await self._create_memory_from_result(agent, skill_name, result)

            return result

        except Exception as e:
            logger.error(f"Agent {agent.name} execution failed: {e}", exc_info=True)

            # Emit agent error event
            await self._emit_event("agent_error", {
                "session_id": self.session_id,
                "agent_id": agent_id,
                "agent_name": agent.name,
                "skill_name": skill_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })

            raise

    async def _plan_research_tasks(self, initial_prompt: str) -> List[AgentTask]:
        """
        Create a plan of tasks to execute for the research workflow.

        Returns task dependency graph.
        """
        tasks = []
        task_counter = 0

        # Find agents by name
        agent_map = {}
        for sa in self.session_agents:
            result = await self.db.execute(
                select(Agent).where(Agent.id == sa.agent_id)
            )
            agent = result.scalar_one_or_none()
            if agent:
                agent_map[agent.name] = agent.id

        # Task 1: Generate hypotheses
        if "hypothesis_agent" in agent_map:
            task_counter += 1
            tasks.append(AgentTask(
                task_id=f"task_{task_counter}",
                agent_id=agent_map["hypothesis_agent"],
                agent_name="hypothesis_agent",
                skill_name="generate_hypotheses",
                input_data={
                    "literature_summary": initial_prompt,
                    "research_gap": "Identified from prompt",
                    "domain": "general",
                },
            ))

        # Task 2: Design experiment (depends on hypotheses)
        if "experiment_agent" in agent_map:
            task_counter += 1
            tasks.append(AgentTask(
                task_id=f"task_{task_counter}",
                agent_id=agent_map["experiment_agent"],
                agent_name="experiment_agent",
                skill_name="design_experiment",
                input_data={
                    "hypothesis": "{{task_1.result}}",  # Placeholder for task 1 result
                    "domain": "general",
                },
                depends_on=["task_1"],
            ))

        # Task 3: Generate code (depends on experiment design)
        if "code_gen_agent" in agent_map:
            task_counter += 1
            tasks.append(AgentTask(
                task_id=f"task_{task_counter}",
                agent_id=agent_map["code_gen_agent"],
                agent_name="code_gen_agent",
                skill_name="generate_code",
                input_data={
                    "experiment_design": "{{task_2.result}}",
                    "domain": "general",
                },
                depends_on=["task_2"],
            ))

        # Task 4: Execute code (depends on code generation)
        if "execution_agent" in agent_map:
            task_counter += 1
            tasks.append(AgentTask(
                task_id=f"task_{task_counter}",
                agent_id=agent_map["execution_agent"],
                agent_name="execution_agent",
                skill_name="execute_experiment",
                input_data={
                    "experiment_id": self.session_id,
                    "code": "{{task_3.result.code}}",
                },
                depends_on=["task_3"],
            ))

        # Task 5: Analyze results (depends on execution)
        if "analysis_agent" in agent_map:
            task_counter += 1
            tasks.append(AgentTask(
                task_id=f"task_{task_counter}",
                agent_id=agent_map["analysis_agent"],
                agent_name="analysis_agent",
                skill_name="analyze_results",
                input_data={
                    "hypothesis": "{{task_1.result}}",
                    "experiment_design": "{{task_2.result}}",
                    "execution_results": "{{task_4.result}}",
                    "domain": "general",
                },
                depends_on=["task_1", "task_2", "task_4"],
            ))

        return tasks

    async def _execute_tasks(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """
        Execute tasks in dependency order.

        Returns:
            Results keyed by task_id
        """
        results = {}
        completed_tasks = set()

        # Store tasks for lookup
        self.tasks = {task.task_id: task for task in tasks}

        while len(completed_tasks) < len(tasks):
            # Find tasks ready to execute (all dependencies completed)
            ready_tasks = [
                task for task in tasks
                if task.task_id not in completed_tasks
                and all(dep in completed_tasks for dep in task.depends_on)
            ]

            if not ready_tasks:
                # Deadlock detection
                pending = [t.task_id for t in tasks if t.task_id not in completed_tasks]
                raise RuntimeError(f"Task dependency deadlock detected. Pending: {pending}")

            # Execute ready tasks in parallel
            task_results = await asyncio.gather(
                *[self._execute_task(task, results) for task in ready_tasks],
                return_exceptions=True,
            )

            # Process results
            for task, result in zip(ready_tasks, task_results):
                if isinstance(result, Exception):
                    logger.error(f"Task {task.task_id} failed: {result}")
                    task.status = "failed"
                    task.error = str(result)
                else:
                    task.status = "completed"
                    task.result = result
                    results[task.task_id] = result

                completed_tasks.add(task.task_id)

        return results

    async def _execute_task(self, task: AgentTask, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        task.status = "running"
        task.started_at = datetime.utcnow()

        # Resolve input data placeholders from previous results
        resolved_input = self._resolve_placeholders(task.input_data, previous_results)

        # Execute agent
        result = await self.execute_single_agent(
            agent_id=task.agent_id,
            skill_name=task.skill_name,
            input_data=resolved_input,
        )

        task.completed_at = datetime.utcnow()
        return result

    def _resolve_placeholders(self, input_data: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve placeholder references to previous task results.

        Placeholders: {{task_X.result.field}}
        """
        import re

        resolved = {}
        for key, value in input_data.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Extract reference path
                ref = value[2:-2].strip()
                parts = ref.split(".")

                # Navigate to referenced value
                current = results
                for part in parts:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        current = getattr(current, part, None)

                resolved[key] = current if current is not None else value
            else:
                resolved[key] = value

        return resolved

    async def _create_cell_from_result(
        self,
        agent: Agent,
        skill_name: str,
        result: Dict[str, Any],
    ) -> None:
        """Create a cell from agent output"""
        # Determine cell type and content based on agent and result
        cell_type = "markdown"
        cell_content = ""

        if "raw_output" in result:
            cell_content = result["raw_output"]
        elif "code" in result:
            cell_type = "code"
            cell_content = result["code"]
        else:
            # Generic JSON output
            import json
            cell_content = json.dumps(result, indent=2)

        # Create cell
        cell = Cell(
            project_id=self.session.project_id,
            cell_type=cell_type,
            content=cell_content,
            metadata={
                "created_by": "agent",
                "agent_id": agent.id,
                "agent_name": agent.name,
                "skill_name": skill_name,
            },
            created_by=self.user_id,
        )
        self.db.add(cell)
        await self.db.flush()

        # Link cell to session
        session_cell = SessionCell(
            session_id=self.session_id,
            cell_id=cell.id,
            position=0,  # Will be updated by frontend
            created_by_agent=agent.name,
        )
        self.db.add(session_cell)
        await self.db.commit()

        # Emit cell created event
        await self._emit_event("cell_created", {
            "session_id": self.session_id,
            "cell_id": str(cell.id),
            "agent_name": agent.name,
            "cell_type": cell_type,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def _create_memory_from_result(
        self,
        agent: Agent,
        skill_name: str,
        result: Dict[str, Any],
    ) -> None:
        """Create a memory from agent execution"""
        content = f"Agent {agent.display_name} executed skill '{skill_name}'"

        if "raw_output" in result:
            content = result["raw_output"]

        memory = SessionMemory(
            session_id=self.session_id,
            project_id=self.session.project_id,
            memory_type="result",
            content=content,
            memory_metadata={
                "agent_id": agent.id,
                "agent_name": agent.name,
                "skill_name": skill_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        self.db.add(memory)
        await self.db.commit()

    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit WebSocket event to user"""
        try:
            await ws_manager.send_to_user(self.user_id, event_type, data)
        except Exception as e:
            logger.error(f"Failed to emit event {event_type}: {e}")

    def _summarize_results(self, results: Dict[str, Any]) -> str:
        """Generate summary of workflow results"""
        summary = f"Executed {len(results)} tasks successfully"
        return summary

    async def close(self) -> None:
        """Close all agent clients"""
        for client in self.agent_clients.values():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing agent client: {e}")
