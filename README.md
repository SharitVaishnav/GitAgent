# GitAgent - Agentic GitHub Automation Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52.2-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql)](https://www.postgresql.org/)

GitAgent is an intelligent, AI-powered GitHub automation platform that enables natural language interactions with GitHub repositories. Built with OpenAI Agents framework, it provides a conversational interface for managing repositories, reviewing pull requests, and automating GitHub workflows.

## 🌟 Features

### 🤖 Intelligent Agent System

GitAgent uses a multi-agent architecture with specialized agents for different tasks:

- **Main Agent**: Orchestrates all GitHub operations and routes requests to specialized agents
- **File Agent**: Handles file content retrieval with intelligent path resolution
- **PR Creation Agent**: Intelligently creates pull requests, automatically detecting fork scenarios
- **PR Review Agent**: Analyzes code changes and provides automated code reviews with feedback

### 🛠️ Comprehensive GitHub Tools

GitAgent provides 16+ GitHub automation tools:

#### Repository Management
- **`list_repos`** - List all repositories for the authenticated user
- **`create_repo`** - Create new repositories with custom settings
- **`delete_repo`** - Delete repositories (with confirmation)
- **`fork_repo`** - Fork repositories to your account
- **`get_repo_info`** - Get detailed repository information and fork status

#### File Operations
- **`list_repo_files`** - Browse repository file structure
- **`get_file_content`** - Read file contents from repositories
- **`cache_repo_structure`** - Cache entire repository structure for faster access

#### Branch Management
- **`create_branch`** - Create new branches from any base branch
- **`list_branches`** - List all branches in a repository

#### Pull Request Operations
- **`create_pull_request`** - Create pull requests with intelligent fork detection
- **`list_pull_requests`** - List open, closed, or all pull requests
- **`get_pr_diff`** - Fetch PR diffs and file changes
- **`review_pull_request`** - Submit PR reviews (approve, request changes, comment)
- **`merge_pull_request`** - Merge PRs with different merge strategies (merge, squash, rebase)

#### User Context
- **`get_user_info`** - Retrieve authenticated user information

### 💬 Natural Language Interface

Interact with GitHub using natural language:

```
"Show me all my repositories"
"Create a new repo called my-awesome-project"
"Fork the tensorflow/tensorflow repository"
"Review PR #42 in my-repo"
"Create a pull request from feature-branch to main"
"List all open PRs in owner/repository"
"Merge PR #15 using squash method"
```

### 🔍 Intelligent PR Review

The PR Review Agent provides comprehensive code analysis:

- ✅ **Code Quality**: Best practices, consistency, style
- 🐛 **Bug Detection**: Potential logic errors and edge cases
- 🔒 **Security Analysis**: Security vulnerabilities and risks
- ⚡ **Performance Review**: Performance implications
- 📝 **Documentation**: Comments and documentation quality
- 🧪 **Testing**: Test coverage assessment
- 🏗️ **Architecture**: Design patterns and structure
- 📛 **Naming Conventions**: Variable and function naming

### 💾 Conversation History

- PostgreSQL-backed chat history storage
- Session management for multi-turn conversations
- Tool execution tracking and logging
- Conversation retrieval for context-aware responses

### 🔐 GitHub OAuth Authentication

- Secure GitHub OAuth 2.0 integration
- Token-based API authentication
- User context management
- Session-based access control

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│                  (streamlit_app.py)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│                    (agents/main.py)                          │
├──────────────────────────┬──────────────────────────────────┤
│  Authentication Layer    │  Database Layer                   │
│  (agents/auth.py)        │  (database/database.py)           │
└──────────────────────────┴──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent System (OpenAI)                     │
│                   (agents/config.py)                         │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Main Agent  │  │  File Agent  │  │   PR Agent   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐                                            │
│  │ PR Review    │                                            │
│  │    Agent     │                                            │
│  └──────────────┘                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Tools (16+)                        │
│                     (tools/*.py)                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    GitHub REST API
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 14 or higher
- GitHub account
- GitHub OAuth App credentials
- Groq API key (for AI model)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/GitAgent.git
   cd GitAgent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**
   
   Install PostgreSQL (macOS):
   ```bash
   brew install postgresql@14
   brew services start postgresql@14
   ```

   Create database:
   ```bash
   createdb chat_history
   ```

5. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # GitHub OAuth
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   
   # Groq API (for AI model)
   GROQ_API_KEY=your_groq_api_key
   
   # PostgreSQL
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=chat_history
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   
   # URLs (for production deployment)
   FRONTEND_URL=http://localhost:8501
   BACKEND_URL=http://localhost:8000
   ```

### GitHub OAuth App Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: GitAgent
   - **Homepage URL**: `http://localhost:8501`
   - **Authorization callback URL**: `http://localhost:8501`
4. Copy the Client ID and Client Secret to your `.env` file

### Running the Application

1. **Start the FastAPI backend**
   ```bash
   cd agents
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py
   ```
   The UI will be available at `http://localhost:8501`

3. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Click "Authorize with GitHub"
   - Grant permissions
   - Start chatting with the agent!

## 📖 Usage Examples

### Repository Management

**List your repositories:**
```
User: "Show me all my repositories"
Agent: [Lists all repositories with details]
```

**Create a new repository:**
```
User: "Create a new repository called awesome-project"
Agent: [Creates repository and provides confirmation]
```

**Fork a repository:**
```
User: "Fork the microsoft/vscode repository"
Agent: [Forks the repository to your account]
```

### File Operations

**Browse repository files:**
```
User: "Show me the files in my-repo"
Agent: [Lists all files and directories]
```

**Read a file:**
```
User: "Show me the content of README.md in my-repo"
Agent: [Displays file content]
```

**Cache repository structure:**
```
User: "Cache the structure of my-large-repo"
Agent: [Recursively caches all files for faster access]
```

### Branch Management

**Create a branch:**
```
User: "Create a branch called feature-auth in my-repo"
Agent: [Creates branch and provides git commands]
```

**List branches:**
```
User: "Show me all branches in my-repo"
Agent: [Lists all branches with details]
```

### Pull Request Operations

**Create a pull request:**
```
User: "Create a PR from feature-branch to main in my-repo"
Agent: [Intelligently creates PR, handling fork scenarios]
```

**List pull requests:**
```
User: "Show me all open PRs in owner/repo"
Agent: [Lists all open pull requests]
```

**Review a pull request:**
```
User: "Review PR #42 in my-repo"
Agent: [Analyzes code, provides feedback, submits review]
```

**Merge a pull request:**
```
User: "Merge PR #15 in my-repo using squash"
Agent: [Merges PR with squash strategy]
```

## 🔧 API Reference

### REST API Endpoints

#### POST `/agent/query`

Process a user query through the agent system.

**Headers:**
```
Authorization: Bearer <github_access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "user": "username",
  "query": "Show me all my repositories",
  "timestamp": "2024-01-09T00:00:00",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "assistant_output": {
    "tools_responses": {
      "tool_0": {
        "tool_name": "list_repos",
        "input": {},
        "output": "..."
      }
    },
    "final_assistant_response": "Here are your repositories..."
  },
  "timestamp": "2024-01-09T00:00:01",
  "status": "success",
  "conv_id": "conversation-id",
  "session_id": "session-id"
}
```

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "timestamp": "2024-01-09T00:00:00"
}
```

## 🗄️ Database Schema

### `session` Table
```sql
CREATE TABLE session (
    session_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `conversation` Table
```sql
CREATE TABLE conversation (
    conv_id SERIAL PRIMARY KEY,
    session_id TEXT REFERENCES session(session_id),
    timestamp TIMESTAMP NOT NULL,
    user_query TEXT NOT NULL,
    assistant_output JSONB NOT NULL
);
```

### `session_chat` Table
```sql
CREATE TABLE session_chat (
    id SERIAL PRIMARY KEY,
    session_id TEXT REFERENCES session(session_id),
    conv_id INTEGER REFERENCES conversation(conv_id),
    timestamp TIMESTAMP NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL
);
```

## 🎯 Agent Capabilities

### Main Agent

The orchestrator that handles all user queries and routes to specialized agents.

**Capabilities:**
- User context management
- Tool selection and execution
- Response generation
- Error handling

### File Agent

Specialized agent for file operations with intelligent path resolution.

**Capabilities:**
- File content retrieval
- Path autocorrection
- Repository structure navigation
- Cached file access

### PR Creation Agent

Intelligent pull request creation with fork detection.

**Capabilities:**
- Automatic fork detection
- Parent repository identification
- PR creation to correct repository
- Branch validation

### PR Review Agent

Automated code review with comprehensive analysis.

**Capabilities:**
- Code quality assessment
- Security vulnerability detection
- Performance analysis
- Best practices validation
- Review submission (approve/request changes/comment)

## 🔒 Security

- **OAuth 2.0**: Secure GitHub authentication
- **Token Management**: Access tokens stored securely in session state
- **API Authorization**: All API requests require valid GitHub token
- **Database Security**: PostgreSQL with connection pooling
- **Environment Variables**: Sensitive data stored in `.env` file

## 🚢 Deployment

### Render Deployment

The project includes a `render.yaml` configuration for easy deployment to Render.

1. Push your code to GitHub
2. Connect your repository to Render
3. Set environment variables in Render dashboard
4. Deploy!

### Environment Variables for Production

Update these in your production environment:
```env
FRONTEND_URL=https://your-app.onrender.com
BACKEND_URL=https://your-api.onrender.com
```

## 🛠️ Development

### Project Structure

```
GitAgent/
├── agents/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Agent system configuration
│   ├── auth.py              # GitHub OAuth verification
│   ├── schemas.py           # Pydantic models
│   ├── file_agent.py        # File operations agent
│   ├── pr_agent.py          # PR creation agent
│   ├── pr_review_agent.py   # PR review agent
│   └── get_chat_history.py  # Chat history retrieval
├── database/
│   ├── database.py          # PostgreSQL operations
│   └── POSTGRES_SETUP.md    # Database setup guide
├── tools/
│   ├── list_repos.py
│   ├── create_repo.py
│   ├── delete_repo.py
│   ├── fork_repo.py
│   ├── get_repo_info.py
│   ├── list_repo_files.py
│   ├── get_file_content.py
│   ├── cache_repo_structure.py
│   ├── create_branch.py
│   ├── list_branches.py
│   ├── create_pull_request.py
│   ├── list_pull_requests.py
│   ├── get_pr_diff.py
│   ├── review_pull_request.py
│   ├── merge_pull_request.py
│   └── fetch_context.py
├── streamlit_app.py         # Streamlit frontend
├── git_auth.py              # GitHub OAuth flow
├── github_apis.py           # GitHub API helpers
├── requirements.txt         # Python dependencies
├── render.yaml              # Render deployment config
└── README.md                # This file
```

### Adding New Tools

1. Create a new file in `tools/` directory
2. Implement the tool function with proper type hints
3. Add tool to `agents/config.py` in the agent's tools list
4. Update agent instructions if needed

Example:
```python
# tools/my_new_tool.py
from agents import RunContextWrapper
from agents.schemas import UserContext

def my_new_tool(
    ctx: RunContextWrapper[UserContext],
    param1: str,
    param2: int
) -> str:
    """
    Tool description for the agent.
    
    Args:
        ctx: User context wrapper
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Result description
    """
    # Implementation
    return "Result"
```

### Adding New Agents

1. Create a new file in `agents/` directory
2. Implement the agent creation function
3. Add agent to `agents/config.py`
4. Register as a tool in the main agent

Example:
```python
# agents/my_agent.py
from agents import Agent, OpenAIProvider
from agents.schemas import UserContext

def create_my_agent():
    provider = OpenAIProvider(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    model = provider.get_model("moonshotai/kimi-k2-instruct-0905")
    
    return Agent[UserContext](
        name="MyAgent",
        instructions="Agent instructions...",
        model=model,
        tools=[...]
    )
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues and questions, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built with [OpenAI Agents](https://github.com/openai/openai-agents-python)
- Powered by [Groq](https://groq.com/) for fast AI inference
- UI built with [Streamlit](https://streamlit.io/)
- API built with [FastAPI](https://fastapi.tiangolo.com/)
- Database powered by [PostgreSQL](https://www.postgresql.org/)

---

**Made with ❤️ by the GitAgent Team**
