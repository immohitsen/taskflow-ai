
import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.getcwd())

from llm.gemini_client import LLMClient
from agents import PlannerAgent
from tools import GitHubTool, NewsTool

# Load env vars
load_dotenv()

async def test_planner():
    print("🚀 Starting Core Logic Test...")
    
    try:
        # 1. Init Client
        print("1. Initializing LLM Client...")
        llm = LLMClient()
        print("✅ LLM Client Initialized")

        # 2. Test Simple Generation
        print("\n2. Testing Simple Text Generation...")
        text = llm.generate("Say 'Hello World'")
        print(f"✅ Response: {text.strip()}")

        # 3. Init Planner
        print("\n3. Initializing Planner Agent...")
        tools = [GitHubTool(), NewsTool()]
        planner = PlannerAgent(llm, tools)
        print("✅ Planner Initialized")

        # 4. Run Plan
        task = "Find the top 3 Python web frameworks on GitHub"
        print(f"\n4. Generating Plan for task: '{task}'...")
        
        plan = await planner.run(task)
        print("✅ Plan Generated Successfully!")
        print(f"Summary: {plan.task_summary}")
        print(f"Steps: {len(plan.steps)}")
        for step in plan.steps:
            print(f" - [{step.step_number}] {step.tool}: {step.description}")

    except Exception:
        print("\n❌ TEST FAILED With Exception:")
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_planner())
