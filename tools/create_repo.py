import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def create_repo(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,
    description: str = "",
    is_private: bool = False
) -> str:
    """
    Create a new GitHub repository for the authenticated user.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Name of the repository to create
        description: Description of the repository (optional)
        is_private: Whether the repository should be private (default: False)
    
    Returns:
        A message indicating the repository creation status with the repository URL
    """
    user_ctx = ctx.context
    
    # Prepare input (what the tool received)
    tool_input = {
        "repo_name": repo_name,
        "description": description,
        "is_private": is_private
    }
    
    try:
        # GitHub API endpoint for creating a repository
        api_url = "https://api.github.com/user/repos"
        
        # Prepare the request payload
        payload = {
            "name": repo_name,
            "description": description,
            "private": is_private,
            "auto_init": True  # Initialize with README
        }
        
        # Make the API request
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json=payload,
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 201:
            # Repository created successfully
            repo_data = response.json()
            repo_url = repo_data.get("html_url", "")
            repo_full_name = repo_data.get("full_name", "")
            clone_url = repo_data.get("clone_url", "")
            ssh_url = repo_data.get("ssh_url", "")
            
            privacy = "private" if is_private else "public"
            
            result = f"""Successfully created {privacy} repository!
- Repository: {repo_full_name}
- Description: {description or 'No description'}
- URL: {repo_url}
- Clone (HTTPS): {clone_url}
- Clone (SSH): {ssh_url}
- Initialized with README: Yes"""
            
        elif response.status_code == 422:
            error_data = response.json()
            error_msg = error_data.get("message", "Validation failed")
            errors = error_data.get("errors", [])
            
            if errors and errors[0].get("message") == "name already exists on this account":
                result = f"Error: A repository named '{repo_name}' already exists in your account. Please choose a different name."
            else:
                result = f"Error: {error_msg}. Please check the repository name and try again."
                
        elif response.status_code == 403:
            result = "Error: You don't have permission to create repositories. This might be due to account limitations or rate limits."
            
        elif response.status_code == 401:
            result = "Error: Authentication failed. Please check your access token."
            
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error creating repository: {error_msg} (Status: {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while creating repository: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "create_repo",
        "input": tool_input,
        "output": result
    })
    
    return result
