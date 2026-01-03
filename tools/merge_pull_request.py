import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def merge_pull_request(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,
    pull_number: int,
    merge_method: str = "merge",
    commit_title: str = "",
    commit_message: str = ""
) -> str:
    """
    Merge a pull request in a GitHub repository.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo'
        pull_number: PR number to merge
        merge_method: Merge method - "merge", "squash", or "rebase" (default: "merge")
        commit_title: Optional custom merge commit title
        commit_message: Optional custom merge commit message
    
    Returns:
        Merge confirmation with commit SHA
    """
    user_ctx = ctx.context
    
    # Parse repository name
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
    else:
        owner = user_ctx.github_username
        repo = repo_name
    
    full_repo_name = f"{owner}/{repo}"
    
    # Validate merge method
    valid_methods = ["merge", "squash", "rebase"]
    if merge_method not in valid_methods:
        merge_method = "merge"
    
    tool_input = {
        "repo_name": full_repo_name,
        "pull_number": pull_number,
        "merge_method": merge_method
    }
    
    try:
        # Merge pull request
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/merge"
        
        payload = {
            "merge_method": merge_method
        }
        
        # Add optional commit title and message
        if commit_title:
            payload["commit_title"] = commit_title
        if commit_message:
            payload["commit_message"] = commit_message
        
        response = requests.put(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            merged = data.get("merged", False)
            sha = data.get("sha", "")
            message = data.get("message", "")
            
            if merged:
                result = f"""Successfully merged pull request!
- PR #{pull_number} in {full_repo_name}
- Merge method: {merge_method}
- Commit SHA: {sha[:7]}
- Message: {message}

The pull request has been merged into the base branch."""
            else:
                result = f"Error: Pull request #{pull_number} could not be merged. {message}"
        
        elif response.status_code == 405:
            result = f"Error: Pull request #{pull_number} is not mergeable. It may have conflicts or required checks are failing."
        
        elif response.status_code == 404:
            result = f"Error: Pull request #{pull_number} not found in repository '{full_repo_name}'."
        
        elif response.status_code == 403:
            result = f"Error: You don't have permission to merge pull requests in '{full_repo_name}'."
        
        elif response.status_code == 409:
            result = f"Error: Pull request #{pull_number} has a merge conflict. Resolve conflicts before merging."
        
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error merging pull request: {error_msg} (Status: {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while merging pull request: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "merge_pull_request",
        "input": tool_input,
        "output": result[:500] if len(result) > 500 else result
    })
    
    return result
