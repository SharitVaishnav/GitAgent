import sys
from pathlib import Path

# Add parent directory to path to allow imports from sibling directories
sys.path.insert(0, str(Path(__file__).parent.parent))
from database.database import get_session_history

def fetch_chat_history(session_id: str) -> str:
    """
    Fetch and format chat history for a session.
    Uses the fast JSONB history column from session_chat table.
    
    Args:
        session_id: Session ID to fetch history for
        
    Returns:
        str: Formatted conversation history for agent context
    """
    if not session_id:
        return ""
    
    # Fetch chat history from database (JSONB column)
    history_dict = get_session_history(session_id)
    
    if not history_dict:
        return ""
    
    # Format history as conversation
    # Sort by timestamp to maintain chronological order
    sorted_conversations = sorted(
        history_dict.items(),
        key=lambda x: x[1].get('timestamp', '')
    )
    
    history_context = "\n[Previous Conversation]\n"
    for conv_id, conv_data in sorted_conversations:
        user_query = conv_data.get('user_query', '')
        assistant_output = conv_data.get('assistant_output', {})
        final_response = assistant_output.get('final_assistant_response', '')
        tools_responses = assistant_output.get('tools_responses', [])
        timestamp = conv_data.get('timestamp', '')
        
        # Include timestamp in the history
        history_context += f"[{timestamp}]\n"
        history_context += f"User: {user_query}\n"
        history_context += f"Tools_Responses: {tools_responses}\n"
        history_context += f"Assistant: {final_response}\n\n"
    
    history_context += "[End of Previous Conversation]\n\n"
    
    return history_context