# AI Operations Assistant

A multi-agent AI system that accepts natural-language tasks, plans execution steps, calls real APIs, and returns structured results.

## 🏗️ Architecture

This project implements a **multi-agent architecture** with three specialized agents:

```
User Task → [Planner Agent] → [Executor Agent] → [Verifier Agent] → Final Response
                  ↓                   ↓                  ↓
              JSON Plan         API Calls          Validation
```

### Agents

| Agent | Responsibility |
|-------|---------------|
| **Planner** | Analyzes user tasks and creates step-by-step execution plans with tool selection |
| **Executor** | Iterates through plan steps, calls appropriate APIs, handles retries |
| **Verifier** | Validates completeness, checks quality, formats final structured output |

### Tools (API Integrations)

| Tool | API | Capabilities |
|------|-----|-------------|
| **GitHub** | GitHub REST API | Search repositories, get repo details (stars, forks, language) |
| **Weather** | OpenWeatherMap API | Get current weather by city (temperature, humidity, conditions) |
| **News** | NewsAPI | Fetch headlines by category, search articles by topic |

### LLM Usage

- **Provider**: OpenAI (GPT-4o-mini)
- **Structured Outputs**: Uses Pydantic models with OpenAI's `response_format` for type-safe responses
- **Non-Monolithic**: Each agent has focused prompts for its specific task

## 📁 Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py      # Abstract base class for agents
│   ├── planner.py         # Planner Agent - generates execution plans
│   ├── executor.py        # Executor Agent - runs tools
│   └── verifier.py        # Verifier Agent - validates & formats
├── tools/
│   ├── __init__.py
│   ├── base_tool.py       # Abstract base class for tools
│   ├── github_tool.py     # GitHub API integration
│   ├── weather_tool.py    # OpenWeatherMap integration
│   └── news_tool.py       # NewsAPI integration
├── llm/
│   ├── __init__.py
│   └── openai_client.py   # OpenAI client with structured outputs
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- API keys for:
  - OpenAI (required)
  - OpenWeatherMap (free tier: https://openweathermap.org/api)
  - NewsAPI (free tier: https://newsapi.org/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_ops_assistant
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your API keys
   ```

   Required environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENWEATHER_API_KEY=your_openweathermap_api_key
   NEWS_API_KEY=your_newsapi_key
   GITHUB_TOKEN=your_github_token  # Optional, increases rate limit
   ```

### Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Example Prompts

Test the system with these example tasks:

### 1. Multi-tool Task (GitHub + Weather)
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Find the top 3 Python web frameworks on GitHub and tell me the weather in San Francisco"}'
```

### 2. GitHub Search
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Search for the most popular machine learning libraries on GitHub"}'
```

### 3. Weather Query
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "What is the current weather in Tokyo, London, and New York?"}'
```

### 4. News Headlines
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Get the latest technology news headlines"}'
```

### 5. Combined Task (All Tools)
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Find trending AI repositories on GitHub, get the weather in Silicon Valley, and show me recent AI news"}'
```

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/tools` | List available tools |
| POST | `/task` | Submit a task for execution |

### POST /task

**Request Body:**
```json
{
  "task": "Your natural language task here"
}
```

**Response:**
```json
{
  "task": "Original task",
  "status": "success|partial|failed",
  "summary": "Brief summary of results",
  "data": {
    "step_1_github": { ... },
    "step_2_weather": { ... }
  },
  "errors": [],
  "plan": {
    "task_summary": "...",
    "steps": [...],
    "expected_output": "..."
  }
}
```

## ⚠️ Known Limitations & Tradeoffs

1. **Rate Limits**: APIs have rate limits (especially GitHub without token and NewsAPI free tier)
2. **Sequential Execution**: Steps execute sequentially; no parallel execution yet
3. **No Caching**: API responses are not cached; repeated queries make new API calls
4. **Context Length**: Very complex tasks may exceed LLM context limits
5. **Error Recovery**: Limited ability to recover from mid-plan failures
6. **No Persistence**: No database; results are not stored

## 🔮 Future Improvements

- [ ] Add caching for API responses (Redis)
- [ ] Implement parallel tool execution
- [ ] Add cost tracking per request
- [ ] Support more tools (Slack, Jira, etc.)
- [ ] Add streaming responses
- [ ] Implement conversation memory
- [ ] Add authentication/rate limiting

## 📄 License

MIT License
