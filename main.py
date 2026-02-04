"""AI Operations Assistant - Main FastAPI Application."""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agents import PlannerAgent, ExecutorAgent, VerifierAgent
from llm.gemini_client import LLMClient
from tools import GitHubTool, WeatherTool, NewsTool

# Load environment variables
load_dotenv()


class TaskRequest(BaseModel):
    """Request model for task submission."""

    task: str = Field(
        description="Natural language task to execute",
        min_length=1,
        examples=[
            "Find the top 3 Python web frameworks on GitHub and get the weather in San Francisco",
            "Search for machine learning repositories and get technology news headlines",
        ],
    )


class TaskResponse(BaseModel):
    """Response model for task results."""

    task: str
    status: str
    summary: str
    data: dict
    errors: list[str]
    plan: dict | None = None


# Global instances
llm_client: LLMClient | None = None
tools: list = []
planner: PlannerAgent | None = None
executor: ExecutorAgent | None = None
verifier: VerifierAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup."""
    global llm_client, tools, planner, executor, verifier

    print("🚀 Initializing AI Operations Assistant v2 (JSON Fix Loaded)...")

    try:
        # Initialize LLM client
        llm_client = LLMClient()
        print("✅ LLM client initialized")

        # Initialize tools
        tools = [GitHubTool(), NewsTool(), WeatherTool()]
        print(f"✅ Tools initialized: {[t.name for t in tools]}")

        # Initialize agents
        planner = PlannerAgent(llm_client, tools)
        executor = ExecutorAgent(llm_client, tools)
        verifier = VerifierAgent(llm_client)
        print("✅ Agents initialized: Planner, Executor, Verifier")

        print("🎯 AI Operations Assistant is ready!")

    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        raise

    yield

    print("👋 Shutting down AI Operations Assistant...")


app = FastAPI(
    title="AI Operations Assistant",
    description="""
    A multi-agent AI system that accepts natural-language tasks, 
    plans execution steps, calls real APIs, and returns structured results.
    
    ## Features
    - **Planner Agent**: Converts tasks into step-by-step plans
    - **Executor Agent**: Executes plans using integrated tools
    - **Verifier Agent**: Validates results and formats output
    
    ## Available Tools
    - **GitHub**: Search repositories, get repo information
    - **Weather**: Get current weather for any city
    - **News**: Fetch latest news headlines and search articles
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Operations Assistant",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST /task": "Submit a natural language task",
            "GET /tools": "List available tools",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_ready": llm_client is not None,
        "tools_count": len(tools),
        "agents_ready": all([planner, executor, verifier]),
    }


@app.get("/tools")
async def list_tools():
    """List all available tools and their capabilities."""
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters_schema,
            }
            for tool in tools
        ]
    }


@app.post("/task", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """
    Execute a natural language task using the multi-agent system.
    
    The task goes through three stages:
    1. **Planning**: The Planner agent analyzes the task and creates a step-by-step plan
    2. **Execution**: The Executor agent runs each step, calling appropriate APIs
    3. **Verification**: The Verifier agent validates results and formats the response
    """
    if not all([planner, executor, verifier]):
        raise HTTPException(
            status_code=503, detail="Service not fully initialized"
        )

    try:
        # Stage 1: Planning
        print(f"\n📋 Planning task: {request.task}")
        plan = await planner.run(user_task=request.task)
        print(f"✅ Plan created with {len(plan.steps)} steps")

        # Stage 2: Execution
        print("⚙️ Executing plan...")
        execution_result = await executor.run(plan=plan)
        print(f"✅ Execution complete. Success: {execution_result.success}")

        # Stage 3: Verification
        print("🔍 Verifying results...")
        final_response = await verifier.run(
            execution_result=execution_result,
            user_task=request.task,
        )
        print("✅ Verification complete")

        return TaskResponse(
            task=final_response.task,
            status=final_response.status,
            summary=final_response.summary,
            data=final_response.data,
            errors=final_response.errors,
            plan={
                "task_summary": plan.task_summary,
                "steps": [
                    {
                        "step": s.step_number,
                        "description": s.description,
                        "tool": s.tool,
                    }
                    for s in plan.steps
                ],
                "expected_output": plan.expected_output,
            },
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error executing task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
