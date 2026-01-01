# Agent API Project Structure

```
agents/
├── main.py          # FastAPI application and endpoints
├── schemas.py       # Pydantic models and dataclasses
├── auth.py          # GitHub authentication utilities
└── config.py        # Agent configuration and initialization
```

## Module Descriptions

### `main.py`
- FastAPI application entry point
- API endpoint definitions (`/`, `/agent/query`, `/health`)
- Agent lifecycle management (startup)

### `schemas.py`
- `UserContext`: Dataclass for user context information
- `AgentQueryRequest`: Request model for agent queries
- `AgentQueryResponse`: Response model for agent queries

### `auth.py`
- `verify_github_token()`: FastAPI dependency for GitHub OAuth verification
- Validates access tokens against GitHub API
- Returns authenticated user information

### `config.py`
- `create_agent_system()`: Initializes and configures the agent
- Agent configuration with UserContext type
- Model provider setup (Groq API)

## Benefits of This Structure

✅ **Separation of Concerns**: Each file has a single, clear responsibility
✅ **Maintainability**: Easy to locate and modify specific functionality
✅ **Reusability**: Modules can be imported and reused
✅ **Testability**: Individual modules can be tested in isolation
✅ **Readability**: Smaller files are easier to understand
