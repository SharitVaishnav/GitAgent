"""
Tools for the agent to access user context and perform actions.
"""
from agents import function_tool, RunContextWrapper

from schemas import UserContext


@function_tool
def get_user_info(ctx: RunContextWrapper[UserContext]) -> str:
    """Get information about the current user."""
    user_ctx = ctx.context
    
    # Prepare input (what the tool received)
    tool_input = {
        "requested_by": user_ctx.github_username
    }
    
    # Execute the tool logic
    info = f"""User Information:
- GitHub Username: {user_ctx.github_username}
- GitHub Name: {user_ctx.github_name or 'Not provided'}
- GitHub ID: {user_ctx.github_id}
- Session ID: {user_ctx.session_id}
- Request Timestamp: {user_ctx.timestamp}"""
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "get_user_info",
        "input": tool_input,
        "output": info
    })
    
    return info
