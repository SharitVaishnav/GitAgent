import requests
from agents import function_tool

GITHUB_API = "https://api.github.com"

# --- Implementation (Callable by other scripts) ---

def get_user_impl(token: str) -> dict:
    """Get GitHub user information using an access token (Internal Implementation)."""
    res = requests.get(
        f"{GITHUB_API}/user",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=10,
    )
    res.raise_for_status()
    return res.json()

