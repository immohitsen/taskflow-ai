"""GitHub API tool for repository operations."""

import os
from typing import Any

import httpx

from .base_tool import BaseTool, ToolResult


class GitHubTool(BaseTool):
    """Tool for interacting with GitHub API."""

    name = "github"
    description = "Search GitHub repositories, get repository information including stars, description, and language"

    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with optional auth."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search", "get_repo"],
                    "description": "Action to perform: 'search' for searching repos, 'get_repo' for getting specific repo info",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for search action) or 'owner/repo' (for get_repo action)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5,
                },
            },
            "required": ["action", "query"],
        }

    async def execute(self, **kwargs) -> ToolResult:
        """Execute GitHub API request."""
        action = kwargs.get("action")
        query = kwargs.get("query")
        limit = kwargs.get("limit", 5)

        if not action or not query:
            return ToolResult(
                success=False, error="Missing required parameters: action and query"
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if action == "search":
                    return await self._search_repos(client, query, limit)
                elif action == "get_repo":
                    return await self._get_repo(client, query)
                else:
                    return ToolResult(
                        success=False, error=f"Unknown action: {action}"
                    )
        except httpx.TimeoutException:
            return ToolResult(success=False, error="GitHub API request timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"GitHub API error: {str(e)}")

    async def _search_repos(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> ToolResult:
        """Search for repositories."""
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": limit}

        response = await client.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        data = response.json()

        repos = []
        for item in data.get("items", [])[:limit]:
            repos.append({
                "name": item["full_name"],
                "description": item.get("description", "No description"),
                "stars": item["stargazers_count"],
                "language": item.get("language", "Unknown"),
                "url": item["html_url"],
            })

        return ToolResult(
            success=True,
            data={"total_count": data.get("total_count", 0), "repositories": repos},
        )

    async def _get_repo(self, client: httpx.AsyncClient, repo_path: str) -> ToolResult:
        """Get information about a specific repository."""
        url = f"{self.base_url}/repos/{repo_path}"

        response = await client.get(url, headers=self._get_headers())
        response.raise_for_status()
        data = response.json()

        return ToolResult(
            success=True,
            data={
                "name": data["full_name"],
                "description": data.get("description", "No description"),
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "language": data.get("language", "Unknown"),
                "open_issues": data["open_issues_count"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "url": data["html_url"],
                "topics": data.get("topics", []),
            },
        )
