"""NewsAPI tool for fetching news headlines."""

import os
from typing import Any

import httpx

from .base_tool import BaseTool, ToolResult


class NewsTool(BaseTool):
    """Tool for fetching news using NewsAPI."""

    name = "news"
    description = "Get latest news headlines by topic, category, or search query"

    def __init__(self):
        self.base_url = "https://newsapi.org/v2"
        self.api_key = os.getenv("NEWS_API_KEY")

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["headlines", "search"],
                    "description": "Action: 'headlines' for top headlines, 'search' for searching articles",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (required for search, optional for headlines)",
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "business",
                        "entertainment",
                        "general",
                        "health",
                        "science",
                        "sports",
                        "technology",
                    ],
                    "description": "News category (for headlines action)",
                },
                "country": {
                    "type": "string",
                    "description": "2-letter country code (e.g., 'us', 'gb', 'in')",
                    "default": "us",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of articles to return",
                    "default": 5,
                },
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs) -> ToolResult:
        """Fetch news articles."""
        action = kwargs.get("action")

        if not action:
            return ToolResult(
                success=False, error="Missing required parameter: action"
            )

        if not self.api_key:
            return ToolResult(
                success=False,
                error="NEWS_API_KEY environment variable is not set",
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if action == "headlines":
                    return await self._get_headlines(client, **kwargs)
                elif action == "search":
                    return await self._search_articles(client, **kwargs)
                else:
                    return ToolResult(
                        success=False, error=f"Unknown action: {action}"
                    )

        except httpx.TimeoutException:
            return ToolResult(success=False, error="News API request timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"News API error: {str(e)}")

    async def _get_headlines(
        self, client: httpx.AsyncClient, **kwargs
    ) -> ToolResult:
        """Get top headlines."""
        url = f"{self.base_url}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": kwargs.get("country", "us"),
            "pageSize": kwargs.get("limit", 5),
        }

        if kwargs.get("category"):
            params["category"] = kwargs["category"]
        if kwargs.get("query"):
            params["q"] = kwargs["query"]

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return ToolResult(
                success=False, error=data.get("message", "Unknown error")
            )

        articles = self._format_articles(data.get("articles", []))
        return ToolResult(
            success=True,
            data={"total_results": data.get("totalResults", 0), "articles": articles},
        )

    async def _search_articles(
        self, client: httpx.AsyncClient, **kwargs
    ) -> ToolResult:
        """Search for articles."""
        query = kwargs.get("query")
        if not query:
            return ToolResult(
                success=False, error="Search query is required for search action"
            )

        url = f"{self.base_url}/everything"
        params = {
            "apiKey": self.api_key,
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": kwargs.get("limit", 5),
            "language": "en",
        }

        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return ToolResult(
                success=False, error=data.get("message", "Unknown error")
            )

        articles = self._format_articles(data.get("articles", []))
        return ToolResult(
            success=True,
            data={"total_results": data.get("totalResults", 0), "articles": articles},
        )

    def _format_articles(self, articles: list) -> list[dict]:
        """Format article data."""
        formatted = []
        for article in articles:
            formatted.append({
                "title": article.get("title", "No title"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "description": article.get("description", "No description"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
            })
        return formatted
