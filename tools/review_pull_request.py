import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def review_pull_request(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,
    pr_number: int,
    event: str,
    body: str = ""
) -> str:
    """
    Submit a review for a pull request.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo'
        pr_number: Pull request number
        event: Review event - "APPROVE", "REQUEST_CHANGES", or "COMMENT"
        body: Review comment/feedback (optional for APPROVE, required for REQUEST_CHANGES)
    
    Returns:
        Success message or error
    """
    user_ctx = ctx.context
    
    # Parse repository name
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
    else:
        owner = user_ctx.github_username
        repo = repo_name
    
    full_repo_name = f"{owner}/{repo}"
    
    # Validate event
    valid_events = ["APPROVE", "REQUEST_CHANGES", "COMMENT"]
    if event.upper() not in valid_events:
        return f"Error: Invalid review event '{event}'. Must be one of: {', '.join(valid_events)}"
    
    event = event.upper()
    
    # Require body for REQUEST_CHANGES
    if event == "REQUEST_CHANGES" and not body:
        return "Error: Review body is required when requesting changes."
    
    tool_input = {
        "repo_name": full_repo_name,
        "pr_number": pr_number,
        "event": event,
        "body": body
    }
    
    try:
        # Submit review
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        payload = {
            "event": event
        }
        
        if body:
            payload["body"] = body
        
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
        
        if response.status_code == 200:
            review_data = response.json()
            review_id = review_data.get("id")
            
            event_msg = {
                "APPROVE": "✅ Approved",
                "REQUEST_CHANGES": "🔄 Requested changes",
                "COMMENT": "💬 Commented"
            }.get(event, event)
            
            result = f"{event_msg} PR #{pr_number} in '{full_repo_name}'\n"
            result += f"Review ID: {review_id}\n"
            if body:
                result += f"Feedback: {body}"
        
        elif response.status_code == 404:
            result = f"Error: Pull request #{pr_number} not found in '{full_repo_name}'."
        
        elif response.status_code == 422:
            error_msg = response.json().get("message", "Validation failed")
            result = f"Error: {error_msg}. You may have already reviewed this PR or you're the PR author."
        
        elif response.status_code == 403:
            result = f"Error: You don't have permission to review this PR."
        
        else:
            error_msg = response.json().get("message", "Unknown error")
            result = f"Error submitting review: {error_msg} (Status: {response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while submitting review: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "review_pull_request",
        "input": tool_input,
        "output": result
    })
    
    return result
