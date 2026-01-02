import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def delete_repo(ctx: RunContextWrapper[UserContext], repo_name: str) -> str:
    """
    Delete a GitHub repository owned by the authenticated user.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Name of the repository to delete (can be 'owner/repo' or just 'repo')
    
    Returns:
        A message indicating the repository deletion status
    """
    user_ctx = ctx.context
    
    # Prepare input (what the tool received)
    tool_input = {
        "repo_name": repo_name
    }
    
    try:
        # Parse repository name
        if "/" in repo_name:
            # Format: owner/repo
            owner, repo = repo_name.split("/", 1)
        else:
            # Just repo name, use authenticated user as owner
            owner = user_ctx.github_username
            repo = repo_name
        
        # GitHub API endpoint for deleting a repository
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        # Make the DELETE request
        response = requests.delete(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 204:
            # Repository deleted successfully (204 No Content)
            result = f"""Successfully deleted repository!
- Repository: {owner}/{repo}
- Status: Permanently deleted
- Note: This action cannot be undone"""
            
        elif response.status_code == 404:
            result = f"Error: Repository '{owner}/{repo}' not found. Please check the repository name and try again."
            
        elif response.status_code == 403:
            result = f"Error: You don't have permission to delete '{owner}/{repo}'. You must be the owner of the repository to delete it."
            
        elif response.status_code == 401:
            result = "Error: Authentication failed. Please check your access token."
            
        else:
            error_msg = response.json().get("message", "Unknown error") if response.text else "Unknown error"
            result = f"Error deleting repository '{owner}/{repo}': {error_msg} (Status: {response.status_code})"
    
    except ValueError as e:
        result = f"Error: Invalid repository name format. Use 'owner/repo' or just 'repo'. {str(e)}"
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while deleting repository: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "delete_repo",
        "input": tool_input,
        "output": result
    })
    
    return result
