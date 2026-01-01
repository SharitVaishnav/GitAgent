"""
Authentication utilities for GitHub OAuth.
"""
import requests
from fastapi import HTTPException


def verify_github_token(access_token: str) -> dict:
    """
    Verify a GitHub access token and return user information.
    
    Args:
        access_token: GitHub OAuth access token
        
    Returns:
        dict: User information from GitHub API
        
    Raises:
        HTTPException: If token is invalid or verification fails
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        response = requests.get(
            "https://api.github.com/user",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired GitHub access token"
            )
        else:
            raise HTTPException(
                status_code=401,
                detail=f"GitHub authentication failed: {response.status_code}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify token with GitHub: {str(e)}"
        )
