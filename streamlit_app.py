import streamlit as st
import time
import requests
import uuid
from datetime import datetime
from git_auth import get_auth_url, exchange_code
from github_apis import get_user_impl

st.set_page_config(
    page_title="GitHub Helper",
    page_icon="🤖",
    layout="wide"  
)

def init_session():
    """Initialize session state variables."""
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None

def call_agent_api(user_query: str, username: str, access_token: str, session_id: str = None) -> dict:
    """
    Call the agent API with a user query.
    
    Args:
        user_query: The query to send to the agent
        username: The username making the request
        access_token: GitHub access token for authentication
        session_id: Optional session ID
        
    Returns:
        dict with 'success' (bool), 'response' (str), 'conv_id' (str), 'tools_responses' (dict), and optional 'error' (str)
    """
    try:
        # Prepare headers with Authorization
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload (no access_token here)
        payload = {
            "user": username,
            "timestamp": datetime.now().isoformat(),
            "query": user_query
        }
        
        if session_id:
            payload["session_id"] = session_id
        
        response = requests.post(
            "http://localhost:8000/agent/query",
            headers=headers,
            json=payload,
            timeout=120  # Increased timeout to 120 seconds for repository caching operations
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract from new nested structure
            assistant_output = data.get("assistant_output", {})
            final_response = assistant_output.get("final_assistant_response", "No response from agent")
            tools_responses = assistant_output.get("tools_responses", {})
            conv_id = data.get("conv_id", "")
            
            return {
                "success": True,
                "response": final_response,
                "conv_id": conv_id,
                "tools_responses": tools_responses
            }
        elif response.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed. Please log out and log in again."
            }
        else:
            return {
                "success": False,
                "error": f"API returned status code {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Could not connect to agent API. Make sure it's running on port 8000."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. The agent took too long to respond."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def render_header():
    """Render the top header with profile info on the right."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("GitHub Agent")

    with col2:
        if st.session_state.user_info:
            user = st.session_state.user_info
            # Create a localized column layout for the profile to align right-ish
            sub_col1, sub_col2 = st.columns([3, 1])
            with sub_col1:
                st.write(f"**{user.get('login', 'User')}**")
                
                # New Session button
                if st.button("🔄 New Session", key="new_session_btn", use_container_width=True):
                    st.session_state.chat_history = []
                    st.session_state.session_id = str(uuid.uuid4())
                    st.success("New session started!")
                    time.sleep(0.5)
                    st.rerun()
                
                # Logout button
                if st.button("Logout", key="logout_btn", use_container_width=True):
                     st.session_state.access_token = None
                     st.session_state.user_info = None
                     st.session_state.chat_history = []
                     st.rerun()
            with sub_col2:
                 if user.get("avatar_url"):
                    st.image(user.get("avatar_url"), width=50)

def main():
    init_session()
    
    # 1. Check for Callback Code (Priority)
    query_params = st.query_params
    code = query_params.get("code")

    if code:
        try:
            with st.spinner("Authenticating..."):
                token_data = exchange_code(code, "http://localhost:8501")
                
                if "error" in token_data:
                    st.error(f"Error: {token_data.get('error_description')}")
                else:
                    # Authenticated: Store in Session State ONLY
                    access_token = token_data["access_token"]
                    st.session_state.access_token = access_token
                    
                    # Fetch User Info
                    user_info = get_user_impl(access_token)
                    st.session_state.user_info = user_info
                    
                    # Generate unique session ID
                    st.session_state.session_id = str(uuid.uuid4())

                    st.success("Successfully authenticated!")
                    st.query_params.clear()
                    time.sleep(1)
                    st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            st.query_params.clear()
            return

    # 2. Render UI
    render_header()
    
    st.divider()

    if st.session_state.access_token and st.session_state.user_info:
        # Authorized UI: Main Command Area
        
        st.markdown("### Chat with AI Assistant")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Call agent API
            username = st.session_state.user_info.get("login", "user")
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = call_agent_api(
                        user_input, 
                        username,
                        st.session_state.access_token,
                        st.session_state.session_id
                    )
                
                if result["success"]:
                    response = result["response"]
                    st.write(response)
                    
                    # Display tool responses if any were used
                    tools_responses = result.get("tools_responses", {})
                    if tools_responses:
                        with st.expander("🔧 Tool Usage Details"):
                            for tool_id, tool_data in tools_responses.items():
                                st.markdown(f"**{tool_data.get('tool_name', 'Unknown Tool')}**")
                                st.json({
                                    "input": tool_data.get("input"),
                                    "output": tool_data.get("output")
                                })
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                else:
                    error_msg = f"❌ Error: {result['error']}"
                    st.error(error_msg)
                    
                    # Add error to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })
            
            # Rerun to update chat display
            st.rerun()

    else:
        # Unauthorized UI: Centered Login Button
        st.markdown("<br><br>", unsafe_allow_html=True) # Spacer
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.warning("Please sign in to continue.")
            try:
                auth_url = get_auth_url("http://localhost:8501")
                st.link_button("Authorize with GitHub", auth_url, use_container_width=True)
            except ValueError as e:
                st.error(f"Configuration Error: {e}")

if __name__ == "__main__":
    main()
