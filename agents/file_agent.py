import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import Agent, OpenAIProvider, RunContextWrapper
from schemas import UserContext
from tools.get_file_content import get_file_content


def create_file_agent():
    """Create a file agent that handles file content retrieval with path validation."""
    provider = OpenAIProvider(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    model = provider.get_model("openai/gpt-oss-120b")
    
    file_agent = Agent[UserContext](
        name="File Agent",
        instructions="""You are a file content retrieval agent.

Your job is to fetch file content from GitHub repositories.

When the user requests a file:
1. Call the get_file_content tool with the provided repository and file path
2. If it succeeds, return the file content
3. If it fails and the path doesn't exist, it will return the list of paths available in the repository, so choose the closest match and call the get_file_content tool again.
4. If it fails with other reason just return the error message.

Always be helpful and provide clear error messages with all available paths when a file is not found.""",
        model=model,
        tools=[get_file_content],
    )
    
    return file_agent
