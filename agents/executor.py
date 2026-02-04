"""Executor Agent - Executes plan steps and calls tools."""

from typing import Any

from llm import LLMClient
from tools import BaseTool, ToolResult

from .base_agent import BaseAgent
from .planner import ExecutionPlan


class StepResult:
    """Result of executing a single step."""

    def __init__(
        self,
        step_number: int,
        tool_name: str,
        success: bool,
        data: Any = None,
        error: str | None = None,
    ):
        self.step_number = step_number
        self.tool_name = tool_name
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "tool": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }


class ExecutionResult:
    """Result of executing the complete plan."""

    def __init__(self, plan: ExecutionPlan):
        self.plan = plan
        self.step_results: list[StepResult] = []
        self.success = True

    def add_step_result(self, result: StepResult):
        self.step_results.append(result)
        if not result.success:
            self.success = False

    def get_step_result(self, step_number: int) -> StepResult | None:
        for result in self.step_results:
            if result.step_number == step_number:
                return result
        return None

    def to_dict(self) -> dict:
        return {
            "task_summary": self.plan.task_summary,
            "success": self.success,
            "steps": [r.to_dict() for r in self.step_results],
        }


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing plan steps."""

    name = "executor"
    MAX_RETRIES = 2

    def __init__(self, llm_client: LLMClient, tools: list[BaseTool]):
        super().__init__(llm_client)
        self.tools = {tool.name: tool for tool in tools}

    async def run(self, plan: ExecutionPlan, **kwargs) -> ExecutionResult:
        """Execute all steps in the plan."""
        result = ExecutionResult(plan)

        for step in plan.steps:
            # Check dependencies
            can_execute = True
            for dep in step.depends_on:
                dep_result = result.get_step_result(dep)
                if dep_result and not dep_result.success:
                    can_execute = False
                    break

            if not can_execute:
                step_result = StepResult(
                    step_number=step.step_number,
                    tool_name=step.tool,
                    success=False,
                    error="Dependency step failed",
                )
            else:
                step_result = await self._execute_step(step)

            result.add_step_result(step_result)

        return result

    async def _execute_step(self, step) -> StepResult:
        """Execute a single step with retry logic."""
        tool = self.tools.get(step.tool)

        if not tool:
            return StepResult(
                step_number=step.step_number,
                tool_name=step.tool,
                success=False,
                error=f"Tool '{step.tool}' not found",
            )

        last_error = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                tool_result: ToolResult = await tool.execute(**step.parameters)

                return StepResult(
                    step_number=step.step_number,
                    tool_name=step.tool,
                    success=tool_result.success,
                    data=tool_result.data,
                    error=tool_result.error,
                )

            except Exception as e:
                last_error = str(e)
                if attempt < self.MAX_RETRIES:
                    continue

        return StepResult(
            step_number=step.step_number,
            tool_name=step.tool,
            success=False,
            error=f"Execution failed after {self.MAX_RETRIES + 1} attempts: {last_error}",
        )
