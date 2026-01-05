import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import Agent, OpenAIProvider
from schemas import UserContext
from tools.create_pull_request import create_pull_request
from tools.get_repo_info import get_repo_info


def create_pr_agent():
    """Create a PR agent that handles both fork and non-fork scenarios."""
    provider = OpenAIProvider(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    model = provider.get_model("meta-llama/llama-4-scout-17b-16e-instruct")
    
    pr_agent = Agent[UserContext](
        name="PR Agent",
        instructions="""Help users create pull requests.

Steps:
1. Call get_repo_info to check if repo is a fork
2. If fork: Ask "PR to original repo or your fork?"
   - Original: Use parent repo with head_repo parameter
   - Own fork: Normal PR within fork
3. If not fork: Normal PR within same repo, with head repo parameter as None.
4. Ask for: branch, target branch, title, description
5. Call create_pull_request

For upstream PRs, use head_repo parameter.""",
        model=model,
        tools=[get_repo_info, create_pull_request],
    )
    
    return pr_agent
