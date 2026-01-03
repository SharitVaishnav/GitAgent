import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def list_pull_requests(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,
    state: str = "open"
) -> str:
    """
    List pull requests in a GitHub repository.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo'
        state: PR state - "open", "closed", or "all" (default: "open")
    
    Returns:
        Formatted list of pull requests
    """
    user_ctx = ctx.context
    
    # Parse repository name
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
    else:
        owner = user_ctx.github_username
        repo = repo_name
    
    full_repo_name = f"{owner}/{repo}"
    
    # Validate state
    if state not in ["open", "closed", "all"]:
        state = "open"
    
    tool_input = {
        "repo_name": full_repo_name,
        "state": state
    }
    
    try:
        # Get pull requests
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            params={
                "state": state,
                "per_page": 50,
                "sort": "created",
                "direction": "desc"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            prs = response.json()
            
            if not prs:
                result = f"No {state} pull requests found in '{full_repo_name}'."
            else:
                result_lines = [f"{state.capitalize()} Pull Requests in {full_repo_name}:\n"]
                
                for pr in prs:
                    number = pr.get("number")
                    title = pr.get("title", "No title")
                    author = pr.get("user", {}).get("login", "Unknown")
                    head = pr.get("head", {}).get("ref", "?")
                    base = pr.get("base", {}).get("ref", "?")
                    is_draft = pr.get("draft", False)
                    url = pr.get("html_url", "")
                    
                    status = "📝 Draft" if is_draft else "✅ Open"
                    if pr.get("state") == "closed":
                        status = "🔀 Merged" if pr.get("merged", False) else "❌ Closed"
                    
                    result_lines.append(f"""  #{number} {status} - {title}
    By: @{author}
    {head} → {base}
    URL: {url}
""")
                
                result_lines.append(f"Total: {len(prs)} pull request(s)")
                result = "\n".join(result_lines)
        
        elif response.status_code == 404:
            result = f"Error: Repository '{full_repo_name}' not found."
        
        elif response.status_code == 403:
            result = f"Error: You don't have permission to access '{full_repo_name}'."
        
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error listing pull requests: {error_msg} (Status: {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while listing pull requests: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "list_pull_requests",
        "input": tool_input,
        "output": result[:500] if len(result) > 500 else result
    })
    
    return result
