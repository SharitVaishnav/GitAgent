import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def list_branches(ctx: RunContextWrapper[UserContext], repo_name: str) -> str:
    """
    List all branches in a GitHub repository.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo'
    
    Returns:
        Formatted list of branches with details
    """
    user_ctx = ctx.context
    
    # Parse repository name
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
    else:
        owner = user_ctx.github_username
        repo = repo_name
    
    full_repo_name = f"{owner}/{repo}"
    
    tool_input = {
        "repo_name": full_repo_name
    }
    
    try:
        # Get all branches
        api_url = f"https://api.github.com/repos/{owner}/{repo}/branches"
        
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            params={"per_page": 100},
            timeout=30
        )
        
        if response.status_code == 200:
            branches = response.json()
            
            if not branches:
                result = f"No branches found in repository '{full_repo_name}'."
            else:
                result_lines = [f"Branches in {full_repo_name}:\n"]
                
                for branch in branches:
                    name = branch.get("name", "Unknown")
                    commit_sha = branch.get("commit", {}).get("sha", "")[:7]
                    protected = "🔒 Protected" if branch.get("protected", False) else ""
                    
                    result_lines.append(f"  • {name} ({commit_sha}) {protected}")
                
                result_lines.append(f"\nTotal branches: {len(branches)}")
                result = "\n".join(result_lines)
        
        elif response.status_code == 404:
            result = f"Error: Repository '{full_repo_name}' not found."
        
        elif response.status_code == 403:
            result = f"Error: You don't have permission to access '{full_repo_name}'."
        
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error listing branches: {error_msg} (Status: {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while listing branches: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "list_branches",
        "input": tool_input,
        "output": result[:500] if len(result) > 500 else result
    })
    
    return result
