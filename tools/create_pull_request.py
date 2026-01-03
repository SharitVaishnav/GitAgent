import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def create_pull_request(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,
    title: str,
    head_branch: str,
    base_branch: str = "main",
    description: str = "",
    draft: bool = False,
    head_repo: str = None
) -> str:
    """
    Create a pull request in a GitHub repository.
    Supports both internal PRs and cross-repository PRs (from forks).
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Target repository name in 'owner/repo' format
        title: PR title
        head_branch: Source branch (the branch with your changes)
        base_branch: Target branch to merge into (default: "main")
        description: PR description/body (optional)
        draft: Create as draft PR (default: False)
        head_repo: Source repository for cross-repo PRs (format: "owner/repo" or "owner:branch")
                   If None, assumes same repository (internal PR)
    
    Returns:
        PR details including number and URL
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
        "repo_name": full_repo_name,
        "title": title,
        "head_branch": head_branch,
        "base_branch": base_branch
    }
    
    try:
        # Determine the head value for the PR
        # For cross-repo PRs (forks), use "owner:branch" format
        # For internal PRs, use just "branch"
        if head_repo:
            # Cross-repository PR (from fork to parent)
            if "/" in head_repo:
                head_owner = head_repo.split("/")[0]
            else:
                head_owner = head_repo
            head_value = f"{head_owner}:{head_branch}"
        else:
            # Internal PR (same repository)
            head_value = head_branch
        
        # Create pull request
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        
        payload = {
            "title": title,
            "head": head_value,
            "base": base_branch,
            "body": description,
            "draft": draft
        }
        
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
        
        if response.status_code == 201:
            pr_data = response.json()
            pr_number = pr_data.get("number")
            pr_url = pr_data.get("html_url")
            is_draft = pr_data.get("draft", False)
            
            result = f"""Successfully created pull request!
- PR #{pr_number}: {title}
- Repository: {full_repo_name}
- From: {head_value} → {base_branch}
- Status: {"Draft" if is_draft else "Open"}
- URL: {pr_url}

Your pull request is ready for review!"""
        
        elif response.status_code == 422:
            error_data = response.json()
            errors = error_data.get("errors", [])
            
            # Check for common errors
            if any("pull request already exists" in str(err).lower() for err in errors):
                result = f"Error: A pull request already exists for {head_value} → {base_branch}."
            elif any("no commits between" in str(err).lower() for err in errors):
                result = f"Error: No commits found between {base_branch} and {head_value}. The branches are identical."
            else:
                result = f"Error: {error_data.get('message', 'Validation failed')}. {errors}"
        
        elif response.status_code == 404:
            result = f"Error: Repository '{full_repo_name}' or branch not found. Make sure both '{head_value}' and '{base_branch}' exist."
        
        elif response.status_code == 403:
            result = f"Error: You don't have permission to create pull requests in '{full_repo_name}'."
        
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error creating pull request: {error_msg} (Status: {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while creating pull request: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "create_pull_request",
        "input": tool_input,
        "output": result[:500] if len(result) > 500 else result
    })
    
    return result
