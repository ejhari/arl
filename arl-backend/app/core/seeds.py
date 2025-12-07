"""Database seed data for system agents"""

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.agent import Agent


# System agents following A2A protocol
SYSTEM_AGENTS = [
    {
        "name": "hypothesis-agent",
        "display_name": "Hypothesis Agent",
        "description": "Generates and refines research hypotheses based on provided context and data. Uses structured reasoning to propose testable hypotheses.",
        "agent_type": "system",
        "is_system": True,
        "is_active": True,
        "version": "1.0.0",
        "protocol_version": "0.3",
        "agent_card": {
            "name": "hypothesis-agent",
            "description": "Generates and refines research hypotheses",
            "url": None,
            "provider": {"organization": "ARL", "url": None},
            "version": "1.0.0",
            "documentationUrl": None,
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": True
            },
            "authentication": {"schemes": []},
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "skills": [
                {
                    "id": "generate_hypothesis",
                    "name": "Generate Hypothesis",
                    "description": "Generate research hypotheses from context",
                    "tags": ["research", "hypothesis", "generation"],
                    "examples": [
                        "Generate hypotheses about the relationship between X and Y",
                        "Propose testable hypotheses based on this data"
                    ]
                },
                {
                    "id": "refine_hypothesis",
                    "name": "Refine Hypothesis",
                    "description": "Refine and improve existing hypotheses",
                    "tags": ["research", "hypothesis", "refinement"]
                }
            ]
        }
    },
    {
        "name": "experiment-agent",
        "display_name": "Experiment Agent",
        "description": "Designs experiments and research methodologies. Creates experimental protocols and suggests appropriate statistical methods.",
        "agent_type": "system",
        "is_system": True,
        "is_active": True,
        "version": "1.0.0",
        "protocol_version": "0.3",
        "agent_card": {
            "name": "experiment-agent",
            "description": "Designs experiments and research methodologies",
            "url": None,
            "provider": {"organization": "ARL", "url": None},
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": True
            },
            "authentication": {"schemes": []},
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "skills": [
                {
                    "id": "design_experiment",
                    "name": "Design Experiment",
                    "description": "Design experimental protocols",
                    "tags": ["research", "experiment", "design"]
                },
                {
                    "id": "suggest_methods",
                    "name": "Suggest Methods",
                    "description": "Suggest appropriate statistical methods",
                    "tags": ["research", "statistics", "methods"]
                }
            ]
        }
    },
    {
        "name": "code-gen-agent",
        "display_name": "Code Generation Agent",
        "description": "Generates code for data analysis, visualization, and automation. Supports Python, R, and SQL code generation.",
        "agent_type": "system",
        "is_system": True,
        "is_active": True,
        "version": "1.0.0",
        "protocol_version": "0.3",
        "agent_card": {
            "name": "code-gen-agent",
            "description": "Generates code for data analysis and automation",
            "url": None,
            "provider": {"organization": "ARL", "url": None},
            "version": "1.0.0",
            "capabilities": {
                "streaming": True,
                "pushNotifications": False,
                "stateTransitionHistory": True
            },
            "authentication": {"schemes": []},
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text", "code"],
            "skills": [
                {
                    "id": "generate_python",
                    "name": "Generate Python Code",
                    "description": "Generate Python code for data analysis",
                    "tags": ["code", "python", "analysis"]
                },
                {
                    "id": "generate_visualization",
                    "name": "Generate Visualization",
                    "description": "Generate code for data visualization",
                    "tags": ["code", "visualization", "charts"]
                },
                {
                    "id": "generate_sql",
                    "name": "Generate SQL",
                    "description": "Generate SQL queries for data extraction",
                    "tags": ["code", "sql", "database"]
                }
            ]
        }
    },
    {
        "name": "execution-agent",
        "display_name": "Execution Agent",
        "description": "Executes code in sandboxed environments. Manages compute resources and returns execution results with logs.",
        "agent_type": "system",
        "is_system": True,
        "is_active": True,
        "version": "1.0.0",
        "protocol_version": "0.3",
        "agent_card": {
            "name": "execution-agent",
            "description": "Executes code in sandboxed environments",
            "url": None,
            "provider": {"organization": "ARL", "url": None},
            "version": "1.0.0",
            "capabilities": {
                "streaming": True,
                "pushNotifications": True,
                "stateTransitionHistory": True
            },
            "authentication": {"schemes": []},
            "defaultInputModes": ["text", "code"],
            "defaultOutputModes": ["text", "data"],
            "skills": [
                {
                    "id": "execute_python",
                    "name": "Execute Python",
                    "description": "Execute Python code in sandbox",
                    "tags": ["execution", "python", "sandbox"]
                },
                {
                    "id": "execute_notebook",
                    "name": "Execute Notebook",
                    "description": "Execute Jupyter notebook cells",
                    "tags": ["execution", "notebook", "jupyter"]
                }
            ]
        }
    },
    {
        "name": "analysis-agent",
        "display_name": "Analysis Agent",
        "description": "Analyzes data and results. Performs statistical analysis, pattern recognition, and generates insights from research data.",
        "agent_type": "system",
        "is_system": True,
        "is_active": True,
        "version": "1.0.0",
        "protocol_version": "0.3",
        "agent_card": {
            "name": "analysis-agent",
            "description": "Analyzes data and generates insights",
            "url": None,
            "provider": {"organization": "ARL", "url": None},
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": True
            },
            "authentication": {"schemes": []},
            "defaultInputModes": ["text", "data"],
            "defaultOutputModes": ["text", "data"],
            "skills": [
                {
                    "id": "statistical_analysis",
                    "name": "Statistical Analysis",
                    "description": "Perform statistical analysis on data",
                    "tags": ["analysis", "statistics", "data"]
                },
                {
                    "id": "pattern_recognition",
                    "name": "Pattern Recognition",
                    "description": "Identify patterns in data",
                    "tags": ["analysis", "patterns", "ml"]
                },
                {
                    "id": "generate_insights",
                    "name": "Generate Insights",
                    "description": "Generate insights from analysis results",
                    "tags": ["analysis", "insights", "summary"]
                }
            ]
        }
    },
    {
        "name": "literature-agent",
        "display_name": "Literature Review Agent",
        "description": "Searches and analyzes academic literature. Summarizes papers, identifies relevant work, and helps with citation management.",
        "agent_type": "system",
        "is_system": True,
        "is_active": True,
        "version": "1.0.0",
        "protocol_version": "0.3",
        "agent_card": {
            "name": "literature-agent",
            "description": "Searches and analyzes academic literature",
            "url": None,
            "provider": {"organization": "ARL", "url": None},
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": True
            },
            "authentication": {"schemes": []},
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "skills": [
                {
                    "id": "search_literature",
                    "name": "Search Literature",
                    "description": "Search academic databases",
                    "tags": ["literature", "search", "academic"]
                },
                {
                    "id": "summarize_paper",
                    "name": "Summarize Paper",
                    "description": "Summarize academic papers",
                    "tags": ["literature", "summary", "papers"]
                },
                {
                    "id": "find_citations",
                    "name": "Find Citations",
                    "description": "Find relevant citations for research",
                    "tags": ["literature", "citations", "references"]
                }
            ]
        }
    }
]


async def seed_system_agents(db: AsyncSession) -> list[Agent]:
    """Seed system agents if they don't exist"""
    created_agents = []

    for agent_data in SYSTEM_AGENTS:
        # Check if agent already exists
        result = await db.execute(
            select(Agent).where(Agent.name == agent_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing agent's card and info
            existing.display_name = agent_data["display_name"]
            existing.description = agent_data["description"]
            existing.agent_card = agent_data["agent_card"]
            existing.version = agent_data["version"]
            existing.protocol_version = agent_data["protocol_version"]
            existing.updated_at = datetime.utcnow()
            created_agents.append(existing)
        else:
            # Create new agent
            agent = Agent(
                id=str(uuid.uuid4()),
                name=agent_data["name"],
                display_name=agent_data["display_name"],
                description=agent_data["description"],
                agent_type=agent_data["agent_type"],
                is_system=agent_data["is_system"],
                is_active=agent_data["is_active"],
                version=agent_data["version"],
                protocol_version=agent_data["protocol_version"],
                agent_card=agent_data["agent_card"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(agent)
            created_agents.append(agent)

    await db.commit()
    return created_agents


async def run_seeds(db: AsyncSession):
    """Run all seed functions"""
    print("🌱 Seeding database...")

    agents = await seed_system_agents(db)
    print(f"✅ Seeded {len(agents)} system agents")

    print("🌱 Database seeding complete!")
