from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class UserContext:
    """Context information about the authenticated user."""
    github_username: str
    model: str
    github_name: Optional[str]
    github_id: int
    session_id: Optional[str]
    timestamp: str
    access_token: str
    tool_executions: List[Dict[str, Any]] = None  # Track tool calls
    repos_cache: Dict[str, Dict[str, Any]] = None  # Cache of repositories with file structures
    
    
    def __post_init__(self):
        """Initialize tool_executions and repos_cache as empty if not provided."""
        if self.tool_executions is None:
            self.tool_executions = []
        if self.repos_cache is None:
            self.repos_cache = {}


class AgentQueryRequest(BaseModel):
    """Request model for agent query endpoint."""
    user: str
    timestamp: str
    query: Optional[str] = None
    session_id: Optional[str] = None


class ToolResponse(BaseModel):
    """Model for individual tool execution response."""
    tool_name: str
    input: Any  # Can be any type including custom classes
    output: Any


class AssistantOutput(BaseModel):
    """Model for complete assistant output including tool responses."""
    tools_responses: Dict[str, ToolResponse]  # Dict keyed by tool execution ID
    final_assistant_response: str


class ConversationEntry(BaseModel):
    """Model for a single conversation entry."""
    conv_id: str
    session_id: str
    timestamp: str
    user_query: str
    assistant_output: AssistantOutput


class AgentQueryResponse(BaseModel):
    """Response model for agent query endpoint."""
    assistant_output: AssistantOutput
    timestamp: str
    status: str
    conv_id: str
    session_id: str
