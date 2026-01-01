import os
import sys
from pathlib import Path

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import Agent, OpenAIProvider
from schemas import UserContext
from tools.fetch_context import get_user_info


def create_agent_system():
    """Create and configure a simple single agent system."""
    provider = OpenAIProvider(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    model = provider.get_model("openai/gpt-oss-120b")
    
    agent = Agent[UserContext](
        name="Assistant",
        instructions="""You are GitHub-Agent, a helpful assistant.

When users ask about themselves, their username, session, or personal information,
use the get_user_info tool to retrieve their context information.

Answer user queries concisely and directly.""",
        model=model,
        tools=[get_user_info],
    )
    
    return agent
