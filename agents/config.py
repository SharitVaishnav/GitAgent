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
from tools.create_branch import create_branch
from tools.list_branches import list_branches
from tools.list_pull_requests import list_pull_requests
from tools.merge_pull_request import merge_pull_request
from file_agent import create_file_agent
from pr_agent import create_pr_agent
from pr_review_agent import create_pr_review_agent


def create_agent_system():
    """Create and configure a simple single agent system."""
    provider = OpenAIProvider(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    model = provider.get_model("moonshotai/kimi-k2-instruct-0905")
    
    file_agent = create_file_agent()
    pr_agent = create_pr_agent()
    pr_review_agent = create_pr_review_agent()
    
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

When users want to create a branch:
- Use create_branch tool to create a new branch from main or another branch
- Provide git commands for them to checkout the branch locally

When users want to see all branches:
- Use list_branches tool to show all branches in the repository

When users want to create a pull request:
- Just call the pr_creation_agent tool
- It will automatically fetch the parent repo if it is forked.

When users want to see pull requests:
- Use list_pull_requests tool to show open, closed, or all PRs
- Default to showing open PRs

When users want to merge a pull request:
- Use merge_pull_request tool with PR number
- Supports merge methods: "merge", "squash", or "rebase"
- Ask for confirmation before merging

When users want to review a pull request:
- Call the pr_review_agent tool
- It will fetch the PR diff, analyze the code changes, and provide intelligent feedback
- It can approve, request changes, or comment on the PR

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
            create_branch,
            list_branches,
            list_pull_requests,
            merge_pull_request,
            pr_agent.as_tool(
                tool_name="pr_creation_agent",
                tool_description="Use this agent to create pull requests. It intelligently handles both fork and non-fork scenarios."
            ),
            pr_review_agent.as_tool(
                tool_name="pr_review_agent",
                tool_description="Use this agent to review pull requests. It fetches PR diffs, analyzes code quality, and submits reviews (approve, request changes, or comment)."
            ),
            file_agent.as_tool(
                tool_name="file_content_agent",
                tool_description="Use this agent to fetch file content from a GitHub repository. Provide repo_name and file_path."
            )
        ],
    )
    
    return agent
