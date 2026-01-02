import os
import requests
import secrets
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("GIT_CLIENT_SECRET")
AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

def get_auth_url(redirect_uri: str) -> str:
    """Generate the GitHub OAuth authorization URL."""
    if not CLIENT_ID:
        raise ValueError("GIT_CLIENT_ID must be set in .env")
        
    state = secrets.token_hex(16)
    return (
        f"{AUTHORIZE_URL}?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=repo delete_repo read:user&"
        f"state={state}"
    )

# Exchange authorization code for an access token
def exchange_code(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Exchange authorization code for an access token."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("GIT_CLIENT_ID and GIT_CLIENT_SECRET must be set in .env")

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri
        },
        headers={"Accept": "application/json"}
    )
    response.raise_for_status()
    return response.json()