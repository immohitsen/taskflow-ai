"""Base agent interface for all agents."""

from abc import ABC, abstractmethod
from typing import Any

from llm import LLMClient


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    name: str = "base_agent"

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Execute the agent's main task."""
        pass
