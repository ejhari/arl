"""Google ADK Agent Service - A2A Protocol compliant agents using Google ADK

Supports multiple LLM providers:
- Anthropic Claude (native ADK support)
- Google Gemini (native ADK support)
- Azure OpenAI, AWS Bedrock, OpenAI (via ADK's LiteLLM integration)
"""

import logging
from typing import Dict, Any, Optional, List, Union
from google.adk.agents import LlmAgent
from google.adk.models.anthropic_llm import Claude
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.base_llm import BaseLlm
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from app.core.config import settings

logger = logging.getLogger(__name__)

# Agent configurations with skills and prompts (using ADK-compatible names)
AGENT_CONFIGS = {
    "hypothesis_agent": {
        "display_name": "Hypothesis Agent",
        "description": "Generates testable scientific hypotheses from research prompts and literature",
        "system_prompt": """You are a Hypothesis Generation Agent for an autonomous research lab.

Your role is to analyze research prompts and literature to generate testable scientific hypotheses.

When given a research topic or literature summary, you should:
1. Identify key research questions and gaps
2. Generate 2-4 testable hypotheses ranked by novelty and feasibility
3. For each hypothesis, provide:
   - A clear statement
   - Rationale based on existing knowledge
   - Predicted outcomes
   - Confidence level (0.0-1.0)

Output your response in well-structured Markdown format with clear sections.""",
        "skills": [
            {
                "id": "generate_hypotheses",
                "name": "Generate Hypotheses",
                "description": "Generate testable hypotheses from research prompts",
            }
        ],
    },
    "experiment_agent": {
        "display_name": "Experiment Designer",
        "description": "Designs rigorous experiments to test hypotheses",
        "system_prompt": """You are an Experiment Design Agent for an autonomous research lab.

Your role is to design rigorous experiments to test hypotheses.

When given a hypothesis, you should:
1. Define the experimental methodology (steps, controls, variables)
2. Specify data collection requirements
3. Outline statistical analysis approach
4. Identify potential confounds and mitigation strategies
5. Estimate resource requirements

Output your response in well-structured Markdown format.""",
        "skills": [
            {
                "id": "design_experiment",
                "name": "Design Experiment",
                "description": "Design experiments to test hypotheses",
            }
        ],
    },
    "code_gen_agent": {
        "display_name": "Code Generator",
        "description": "Generates executable Python code for experiments",
        "system_prompt": """You are a Code Generation Agent for an autonomous research lab.

Your role is to generate executable Python code for experiments.

When given an experiment design, you should:
1. Write clean, well-documented Python code
2. Include necessary imports
3. Implement data generation/loading
4. Implement the core experimental logic
5. Include visualization code where appropriate
6. Add error handling and logging

Output executable Python code with clear docstrings and comments.""",
        "skills": [
            {
                "id": "generate_code",
                "name": "Generate Code",
                "description": "Generate Python code for experiments",
            }
        ],
    },
    "execution_agent": {
        "display_name": "Execution Engine",
        "description": "Simulates experiment execution and reports results",
        "system_prompt": """You are an Execution Agent for an autonomous research lab.

Your role is to simulate experiment execution and report results.

When given experiment code and parameters, you should:
1. Describe what would happen when the code executes
2. Generate realistic simulated results based on the hypothesis
3. Report execution metrics (time, resources, success rate)
4. Identify any issues or anomalies

Output your response in Markdown format with clear sections.""",
        "skills": [
            {
                "id": "execute_experiment",
                "name": "Execute Experiment",
                "description": "Execute experiments and report results",
            }
        ],
    },
    "analysis_agent": {
        "display_name": "Analysis Agent",
        "description": "Analyzes experimental results and draws conclusions",
        "system_prompt": """You are an Analysis Agent for an autonomous research lab.

Your role is to analyze experimental results and draw conclusions.

When given hypothesis, experiment design, and execution results, you should:
1. Perform statistical analysis of results
2. Evaluate whether the hypothesis is supported
3. Identify patterns and insights
4. Suggest follow-up experiments
5. Summarize key findings

Output your response in Markdown format with clear sections.""",
        "skills": [
            {
                "id": "analyze_results",
                "name": "Analyze Results",
                "description": "Analyze experimental results",
            }
        ],
    },
    "literature_agent": {
        "display_name": "Literature Review Agent",
        "description": "Synthesizes research literature and identifies knowledge gaps",
        "system_prompt": """You are a Literature Review Agent for an autonomous research lab.

Your role is to synthesize research literature and identify knowledge gaps.

When given a research topic, you should:
1. Summarize key findings from relevant research areas
2. Identify consensus and controversies
3. Highlight methodological approaches
4. Point out gaps and opportunities
5. Suggest relevant citations

Output your response in Markdown format with clear sections.""",
        "skills": [
            {
                "id": "review_literature",
                "name": "Review Literature",
                "description": "Review and synthesize literature",
            }
        ],
    },
}


def get_llm_model() -> BaseLlm:
    """
    Get the LLM model instance for Google ADK based on configured provider.

    Returns native ADK models for Anthropic and Google, uses LiteLLM for others.
    """
    provider = settings.LLM_PROVIDER
    model = settings.LLM_MODEL

    if provider == "anthropic":
        # Native Anthropic support in ADK
        logger.info(f"Using native ADK Claude model: {model}")
        return Claude(model=model)

    elif provider == "google" or provider == "gemini":
        # Native Google/Gemini support in ADK
        logger.info(f"Using native ADK Gemini model: {model}")
        return Gemini(model=model)

    elif provider == "azure":
        # Azure OpenAI via ADK's LiteLLM
        logger.info(f"Using ADK LiteLLM for Azure: {model}")
        return LiteLlm(model=f"azure/{model}")

    elif provider == "bedrock":
        # AWS Bedrock via ADK's LiteLLM
        logger.info(f"Using ADK LiteLLM for Bedrock: {model}")
        return LiteLlm(model=f"bedrock/{model}")

    elif provider == "openai":
        # OpenAI via ADK's LiteLLM
        logger.info(f"Using ADK LiteLLM for OpenAI: {model}")
        return LiteLlm(model=model)

    else:
        # Default to Gemini
        logger.info("Defaulting to Gemini model")
        return Gemini(model="gemini-2.0-flash")


def get_llm_model_name() -> str:
    """Get the model name string for logging/display."""
    provider = settings.LLM_PROVIDER
    model = settings.LLM_MODEL
    return f"{provider}/{model}"


def build_agent_card(agent_name: str, config: Dict[str, Any]) -> AgentCard:
    """Build an A2A AgentCard for an agent."""
    skills = [
        AgentSkill(
            id=skill["id"],
            name=skill["name"],
            description=skill["description"],
            tags=skill.get("tags", ["research", "arl"]),
        )
        for skill in config.get("skills", [])
    ]

    return AgentCard(
        name=agent_name,
        description=config["description"],
        version="1.0.0",
        url=f"http://localhost:8000/api/v1/agents/{agent_name}",  # Required field
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,
        ),
        defaultInputModes=["text"],  # Required field
        defaultOutputModes=["text"],  # Required field
        skills=skills,
    )


class ADKAgentService:
    """
    Service for managing Google ADK agents with A2A protocol support.

    This service creates LlmAgent instances using Google ADK and provides
    a unified interface for calling agent skills.
    """

    def __init__(self):
        self._agents: Dict[str, LlmAgent] = {}
        self._agent_cards: Dict[str, AgentCard] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all ADK agents."""
        if self._initialized:
            return

        model_name = get_llm_model_name()
        logger.info(f"Initializing ADK agents with model: {model_name}")

        # Get the LLM model instance (native for Anthropic/Google, LiteLLM for others)
        try:
            llm_model = get_llm_model()
            logger.info(f"LLM model instance created: {type(llm_model).__name__}")
        except Exception as e:
            logger.error(f"Failed to create LLM model: {e}")
            llm_model = None

        for agent_name, config in AGENT_CONFIGS.items():
            try:
                # Create LlmAgent instance with model object
                agent = LlmAgent(
                    name=agent_name,
                    model=llm_model if llm_model else model_name,
                    instruction=config["system_prompt"],
                    description=config["description"],
                )
                self._agents[agent_name] = agent

                # Build AgentCard
                self._agent_cards[agent_name] = build_agent_card(agent_name, config)

                logger.info(f"Initialized ADK agent: {agent_name}")

            except Exception as e:
                logger.error(f"Failed to initialize ADK agent {agent_name}: {e}")

        self._initialized = True
        logger.info(f"ADK Agent Service initialized with {len(self._agents)} agents")

    def get_agent(self, agent_name: str) -> Optional[LlmAgent]:
        """Get an ADK agent by name."""
        if not self._initialized:
            self.initialize()
        return self._agents.get(agent_name)

    def get_agent_card(self, agent_name: str) -> Optional[AgentCard]:
        """Get an agent's A2A card."""
        if not self._initialized:
            self.initialize()
        return self._agent_cards.get(agent_name)

    def list_agents(self) -> List[str]:
        """List all available agent names."""
        return list(AGENT_CONFIGS.keys())

    def is_configured(self) -> bool:
        """Check if ADK service has valid LLM credentials configured."""
        provider = settings.LLM_PROVIDER

        if provider == "anthropic":
            return bool(settings.ANTHROPIC_API_KEY)
        elif provider in ("google", "gemini"):
            return bool(settings.GOOGLE_API_KEY)
        elif provider == "azure":
            return bool(settings.AZURE_API_KEY and settings.AZURE_API_BASE)
        elif provider == "bedrock":
            return bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)
        elif provider == "openai":
            return bool(settings.OPENAI_API_KEY)

        return False

    async def call_agent(
        self,
        agent_name: str,
        skill_name: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Call an agent skill using ADK.

        Accepts both hyphenated (DB) and underscored (ADK) agent names.
        """
        if not self._initialized:
            self.initialize()

        # Use get_agent which handles name mapping
        agent = self.get_agent(agent_name)
        if not agent:
            return {
                "status": "error",
                "error": f"Agent {agent_name} not found",
                "raw_output": f"# Error\n\nAgent {agent_name} not found",
            }

        try:
            # Build prompt from input data
            prompt = self._build_prompt(skill_name, input_data)

            # Call agent via ADK (using Runner)
            from google.adk import Runner

            runner = Runner(agent=agent, app_name="arl-research")
            session = await runner.session_service.create_session(
                app_name="arl-research",
                user_id="system",
            )

            # Send message and get response
            response = await runner.run_async(
                session_id=session.id,
                user_id="system",
                new_message=prompt,
            )

            # Extract response content
            raw_output = ""
            async for event in response:
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "text"):
                        raw_output += event.content.text

            return {
                "status": "success",
                "raw_output": raw_output,
                "agent_name": agent_name,
                "skill_name": skill_name,
                "model_used": get_llm_model_name(),
            }

        except Exception as e:
            logger.error(f"ADK agent call failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "raw_output": f"# Error\n\nFailed to execute {skill_name}: {str(e)}",
            }

    def _build_prompt(self, skill_name: str, input_data: Dict[str, Any]) -> str:
        """Build a prompt from skill name and input data."""
        prompts = {
            "generate_hypotheses": """Based on the following research context, generate testable hypotheses.

**Research Topic/Literature Summary:**
{literature_summary}

**Research Gap Identified:**
{research_gap}

**Domain:**
{domain}

Please generate 2-4 hypotheses with confidence scores and rationale.""",

            "design_experiment": """Design an experiment to test the following hypothesis.

**Hypothesis:**
{hypothesis}

**Domain:**
{domain}

Please provide a detailed experimental design.""",

            "generate_code": """Generate Python code to implement the following experiment.

**Experiment Design:**
{experiment_design}

**Domain:**
{domain}

Please provide clean, executable Python code.""",

            "execute_experiment": """Simulate the execution of the following experiment.

**Experiment ID:** {experiment_id}

**Code to Execute:**
```python
{code}
```

Please describe the execution and provide simulated results.""",

            "analyze_results": """Analyze the following experimental results.

**Original Hypothesis:**
{hypothesis}

**Experiment Design:**
{experiment_design}

**Execution Results:**
{execution_results}

**Domain:**
{domain}

Please provide a comprehensive analysis.""",
        }

        template = prompts.get(skill_name, str(input_data))
        try:
            return template.format(**input_data)
        except KeyError:
            return f"Skill: {skill_name}\nInput: {input_data}"


# Global service instance
adk_agent_service = ADKAgentService()


def create_a2a_app(agent_name: str, host: str = "localhost", port: int = 8001):
    """
    Create a standalone A2A server for an agent.

    This can be used to run agents as separate microservices.

    Example:
        app = create_a2a_app("hypothesis_agent", port=8001)
        # Run with: uvicorn app:app --host localhost --port 8001
    """
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    adk_agent_service.initialize()
    agent = adk_agent_service.get_agent(agent_name)
    agent_card = adk_agent_service.get_agent_card(agent_name)

    if not agent:
        raise ValueError(f"Agent {agent_name} not found")

    return to_a2a(
        agent,
        host=host,
        port=port,
        protocol="http",
        agent_card=agent_card,
    )
