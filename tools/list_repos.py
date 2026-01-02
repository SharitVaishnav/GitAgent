import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def list_repos(ctx: RunContextWrapper[UserContext]) -> str:
    """
    List GitHub repositories for a user.
    
    Args:
        ctx: The run context wrapper containing user context
        username: GitHub username to fetch repos for (defaults to authenticated user)
        repo_type: Type of repositories to list - 'all', 'owner', 'public', 'private', 'member'
    
    Returns:
        A formatted list of repositories with details
    """
    user_ctx = ctx.context
    
    # Use authenticated user if no username provided
    target_user = user_ctx.github_username

    username = user_ctx.github_username
    
    # Prepare input (what the tool received)
    tool_input = None
    
    try:
        # Determine the API endpoint
        if username is None or username == user_ctx.github_username:
            # Fetch authenticated user's repos (can include private repos)
            api_url = "https://api.github.com/user/repos"
            params = {
                "type": "all",
                "sort": "updated",
                "per_page": 100
            }
        else:
            # Fetch public repos for another user
            api_url = f"https://api.github.com/users/{target_user}/repos"
            params = {
                "type": "all",
                "sort": "updated",
                "per_page": 100
            }
        
        # Make the API request
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            params=params,
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            repos = response.json()
            
            if not repos:
                result = f"No repositories found for user '{target_user}'"
            else:
                # Format the repository list
                repo_list = [f"Found {len(repos)} repositories for '{target_user}':\n"]
                
                for idx, repo in enumerate(repos, 1):
                    name = repo.get("name", "Unknown")
                    full_name = repo.get("full_name", "")
                    description = repo.get("description", "No description")
                    stars = repo.get("stargazers_count", 0)
                    forks = repo.get("forks_count", 0)
                    language = repo.get("language", "N/A")
                    is_private = repo.get("private", False)
                    html_url = repo.get("html_url", "")
                    updated_at = repo.get("updated_at", "")
                    
                    privacy = "🔒 Private" if is_private else "🌐 Public"
                    
                    repo_list.append(f"""
{idx}. {full_name} ({privacy})
   Description: {description}
   Language: {language} | ⭐ {stars} | 🍴 {forks}
   URL: {html_url}
   Last updated: {updated_at}""")
                
                result = "\n".join(repo_list)
                
        elif response.status_code == 404:
            result = f"Error: User '{target_user}' not found on GitHub"
            
        elif response.status_code == 403:
            result = "Error: API rate limit exceeded or insufficient permissions"
            
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error fetching repositories: {error_msg} (Status: {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while fetching repositories: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "list_repos",
        "input": tool_input,
        "output": result
    })
    
    return result
