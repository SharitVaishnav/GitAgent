"""
GitHub Agent API - Main application entry point.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to allow imports from sibling directories
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from agents import Runner

from schemas import AgentQueryRequest, AgentQueryResponse, UserContext, AssistantOutput, ToolResponse
from auth import verify_github_token
from config import create_agent_system
from database.database import init_database, save_conversation, create_session
from get_chat_history import fetch_chat_history

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="GitHub Agent API", version="1.0.0")

# Global agent instance
agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize the agent system and database on startup."""
    global agent
    
    # Initialize database
    init_database()
    
    # Initialize agent
    agent = create_agent_system()
    print("Agent API Ready.")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "GitHub Agent API is running"}


@app.post("/agent/query", response_model=AgentQueryResponse)
async def process_agent_query(
    request: AgentQueryRequest,
    authorization: str = Header(None)
):
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent system not initialized")
        
        # Extract and validate access token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid Authorization header. Expected format: 'Bearer <token>'"
            )
        
        access_token = authorization.split(" ", 1)[1]
        
        # Verify GitHub token and get user info
        user_info = verify_github_token(access_token)
        
        if request.session_id:
            # Ensure session exists in database
            create_session(request.session_id, user_info.get('login', 'unknown'))
        
        # Create user context
        ctx = UserContext(
            github_username=user_info.get('login', 'unknown'),
            github_name=user_info.get('name'),
            github_id=user_info.get('id', 0),
            session_id=request.session_id,
            timestamp=request.timestamp,
            access_token=access_token,
            model="openai/gpt-oss-120b"
        )
        
        # Get the user query
        user_query = request.query if request.query else f"Hello from {request.user}"
        

        # Fetch and format chat history
        history_context = fetch_chat_history(ctx.session_id)
        
        # Combine history with current query
        full_query = f"{history_context}[Current Query]\n{user_query}"
        
        # Run the agent with context and query separately
        result = await Runner.run(
            agent,
            full_query,
            context=ctx
        )
        
        # Extract tool responses from context (tools track themselves)
        tools_responses = {}
        for idx, execution in enumerate(ctx.tool_executions):
            tool_key = f"tool_{idx}"
            tools_responses[tool_key] = execution

        
        # Structure the assistant output
        assistant_output_dict = {
            "tools_responses": tools_responses,
            "final_assistant_response": result.final_output
        }
        
        # Save conversation to database (updates both tables)
        conv_id = save_conversation(
            session_id=ctx.session_id,
            user_query=user_query,
            assistant_output=assistant_output_dict,
            timestamp=ctx.timestamp
        )
        
        # Create AssistantOutput object for response
        assistant_output_obj = AssistantOutput(
            tools_responses=tools_responses,
            final_assistant_response=result.final_output
        )
        # Return the response
        return AgentQueryResponse(
            assistant_output=assistant_output_obj,
            timestamp=datetime.now().isoformat(),
            status="success",
            conv_id=conv_id,
            session_id=ctx.session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)