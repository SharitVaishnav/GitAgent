import os
import sys
from pathlib import Path

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import Agent, OpenAIProvider,RunContextWrapper
from schemas import UserContext
from tools.fetch_context import get_user_info
from tools.list_repos import list_repos
from tools.fork_repo import fork_repo
from tools.create_repo import create_repo
from tools.delete_repo import delete_repo
from tools.list_repo_files import list_repo_files
from tools.cache_repo_structure import cache_repo_structure
from tools.get_file_content import get_file_content
from file_agent import create_file_agent


def create_agent_system():
    """Create and configure a simple single agent system."""
    provider = OpenAIProvider(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    model = provider.get_model("openai/gpt-oss-120b")
    
    file_agent = create_file_agent()
    
    # Create main agent with file_agent as a tool
    agent = Agent[UserContext](
        name="Assistant",
        instructions="""You are GitHub-Agent, a helpful assistant.

When users ask about themselves, their username, session, or personal information,
use the get_user_info tool to retrieve their context information.

When users ask about repositories, use the list_repos tool to retrieve their repository list.

When users ask to fork a repository, use the fork_repo tool to fork the repository.

When users ask to create a new repository, use the create_repo tool to create the repository.

When users ask to delete a repository, use the delete_repo tool to delete the repository, but before calling the function tool, ask the user for confirmation.

When users ask to see files or browse a repository's contents, use the list_repo_files tool to list files and directories.

When users ask to open or read a file:
1. FIRST call cache_repo_structure to cache the repository (if not already cached)
2. THEN call file_content_agent with the repository name and file path

The file_content_agent will automatically provide all available file paths if the requested path doesn't exist.
Use this information to find the correct path and retry.

When users want to cache or index repository structures for faster access, use the cache_repo_structure tool to recursively fetch and store all files and directories.

Answer user queries concisely and directly.""",
        model=model,
        tools=[
            get_user_info, 
            list_repos, 
            fork_repo, 
            create_repo, 
            delete_repo, 
            list_repo_files, 
            cache_repo_structure,
            file_agent.as_tool(
                tool_name="file_content_agent",
                tool_description="Use this agent to fetch file content from a GitHub repository. Provide repo_name and file_path."
            )
        ],
    )
    
    return agent
