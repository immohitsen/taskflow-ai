"""Verifier Agent - Validates results and formats final output."""

import json
from typing import Any

from pydantic import BaseModel, Field

from llm import LLMClient

from .base_agent import BaseAgent
from .executor import ExecutionResult


class VerificationResult(BaseModel):
    """Result of verification process."""

    is_complete: bool = Field(description="Whether the task was fully completed")
    missing_data: list[str] = Field(
        default_factory=list,
        description="List of missing or incomplete data items",
    )
    quality_score: int = Field(
        description="Quality score from 1-10",
        ge=1,
        le=10,
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for improvement",
    )


class FinalResponse(BaseModel):
    """Final structured response to the user."""

    task: str = Field(description="Original task description")
    status: str = Field(description="Overall status: success, partial, or failed")
    summary: str = Field(description="Brief summary of results")
    data: dict[str, Any] = Field(description="Structured data from execution")
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered",
    )


class VerifierAgent(BaseAgent):
    """Agent responsible for verifying and formatting results."""

    name = "verifier"

    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client)

    async def run(
        self, execution_result: ExecutionResult, user_task: str, **kwargs
    ) -> FinalResponse:
        """Verify execution results and generate final response."""
        # First, verify the results
        verification = await self._verify_results(execution_result, user_task)

        # Then, format the final response
        final_response = await self._format_response(
            execution_result, user_task, verification
        )

        return final_response

    async def _verify_results(
        self, execution_result: ExecutionResult, user_task: str
    ) -> VerificationResult:
        """Verify the completeness and quality of results."""
        system_prompt = """You are a verification agent that checks execution results.
Analyze the results and determine:
1. Whether the task was fully completed
2. What data might be missing
3. Overall quality of the results (1-10)
4. Any suggestions for improvement

You must return a valid JSON object matching this structure:
{
    "is_complete": true,
    "missing_data": ["item1", "item2"],
    "quality_score": 8,
    "suggestions": ["suggestion1", "suggestion2"]
}

Be objective and thorough in your assessment."""

        # Build context from execution results
        results_summary = json.dumps(execution_result.to_dict(), indent=2)

        prompt = f"""Verify the following execution results:

Original Task: {user_task}

Execution Results:
{results_summary}

Analyze completeness, identify missing data, and rate quality."""

        verification = self.llm.generate_structured(
            prompt=prompt,
            response_model=VerificationResult,
            system_prompt=system_prompt,
        )

        return verification

    async def _format_response(
        self,
        execution_result: ExecutionResult,
        user_task: str,
        verification: VerificationResult,
    ) -> FinalResponse:
        """Format the final response for the user."""
        system_prompt = """You are a response formatting agent.
Create a clear, well-structured final response that:
1. Summarizes what was accomplished
2. Presents the data in a useful format
3. Notes any errors or limitations
4. Is concise but complete

Format data appropriately based on its type (lists, tables, etc.)."""

        results_summary = json.dumps(execution_result.to_dict(), indent=2)
        verification_summary = verification.model_dump_json(indent=2)

        prompt = f"""Create a final response for this task:

Task: {user_task}

Execution Results:
{results_summary}

Verification:
{verification_summary}

Generate a well-formatted final response."""

        # Determine status
        if execution_result.success and verification.is_complete:
            status = "success"
        elif any(r.success for r in execution_result.step_results):
            status = "partial"
        else:
            status = "failed"

        # Collect successful data
        data = {}
        errors = []

        for step_result in execution_result.step_results:
            if step_result.success and step_result.data:
                data[f"step_{step_result.step_number}_{step_result.tool_name}"] = (
                    step_result.data
                )
            elif step_result.error:
                errors.append(f"Step {step_result.step_number}: {step_result.error}")

        # Generate summary using LLM
        summary_prompt = f"""Summarize these results in 2-3 sentences:
Task: {user_task}
Status: {status}
Data collected: {json.dumps(data, indent=2)}
Errors: {errors}"""

        summary = self.llm.generate(summary_prompt, system_prompt="Be concise and informative.")

        return FinalResponse(
            task=user_task,
            status=status,
            summary=summary,
            data=data,
            errors=errors,
        )
