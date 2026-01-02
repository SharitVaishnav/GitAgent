import requests
from agents import RunContextWrapper, function_tool
from agents.schemas import UserContext


@function_tool
def fork_repo(ctx: RunContextWrapper[UserContext], repo_url: str) -> str:
    """
    Fork a GitHub repository to the authenticated user's account.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_url: The GitHub repository URL (e.g., 'https://github.com/owner/repo' or 'owner/repo')
    
    Returns:
        A message indicating the fork status with the forked repository URL
    """
    user_ctx = ctx.context
    
    # Prepare input (what the tool received)
    tool_input = {
        "repo_url": repo_url
    }
    
    try:
        # Parse the repository owner and name from the URL
        if repo_url.startswith("http"):
            # Extract owner/repo from URL like https://github.com/owner/owner/repo
            parts = repo_url.rstrip("/").split("/")
            if len(parts) < 2:
                raise ValueError("Invalid repository URL format")
            owner, repo = parts[-2], parts[-1]
        else:
            # Handle owner/repo format directly
            parts = repo_url.split("/")
            if len(parts) != 2:
                raise ValueError("Invalid repository format. Use 'owner/repo' or full GitHub URL")
            owner, repo = parts
        
        # Remove .git suffix if present
        repo = repo.replace(".git", "")
        
        # GitHub API endpoint for forking
        api_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
        
        # Make the fork request
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 202:
            # Fork created successfully
            fork_data = response.json()
            forked_repo_url = fork_data.get("html_url", "")
            forked_repo_name = fork_data.get("full_name", "")
            
            result = f"""Successfully forked repository!
- Original: {owner}/{repo}
- Forked to: {forked_repo_name}
- URL: {forked_repo_url}
- Status: Fork is being created (this may take a few moments)"""
            
        elif response.status_code == 403:
            result = f"Error: You don't have permission to fork {owner}/{repo}. The repository might be private or you may have reached the fork limit."
            
        elif response.status_code == 404:
            result = f"Error: Repository {owner}/{repo} not found. Please check the repository name and try again."
            
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error forking repository {owner}/{repo}: {error_msg} (Status: {response.status_code})"
    
    except ValueError as e:
        result = f"Error: {str(e)}"
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while forking repository: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "fork_repo",
        "input": tool_input,
        "output": result
    })
    
    return result