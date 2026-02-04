"""Base tool interface for all API integrations."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Standard result format for all tools."""

    success: bool
    data: Any = None
    error: str | None = None

    def to_context(self) -> str:
        """Convert result to string context for LLM."""
        if self.success:
            return f"Success: {self.data}"
        return f"Error: {self.error}"


class BaseTool(ABC):
    """Abstract base class for all tools."""

    name: str = "base_tool"
    description: str = "Base tool description"

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """Return JSON schema for tool parameters."""
        pass

    def get_tool_info(self) -> dict[str, Any]:
        """Get tool information for the planner."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
        }
