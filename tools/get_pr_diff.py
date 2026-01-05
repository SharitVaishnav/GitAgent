import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def get_pr_diff(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,
    pr_number: int
) -> str:
    """
    Get the diff and changed files for a pull request.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo'
        pr_number: Pull request number
    
    Returns:
        Formatted diff with file changes
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
        "pr_number": pr_number
    }
    
    try:
        # Get PR details
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        
        pr_response = requests.get(
            pr_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30
        )
        
        if pr_response.status_code != 200:
            if pr_response.status_code == 404:
                result = f"Error: Pull request #{pr_number} not found in '{full_repo_name}'."
            else:
                error_msg = pr_response.json().get("message", "Unknown error")
                result = f"Error fetching PR: {error_msg} (Status: {pr_response.status_code})"
            
            user_ctx.tool_executions.append({
                "tool_name": "get_pr_diff",
                "input": tool_input,
                "output": result
            })
            return result
        
        pr_data = pr_response.json()
        
        # Get PR files
        files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        files_response = requests.get(
            files_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            params={"per_page": 100},
            timeout=30
        )
        
        if files_response.status_code != 200:
            error_msg = files_response.json().get("message", "Unknown error")
            result = f"Error fetching PR files: {error_msg}"
            
            user_ctx.tool_executions.append({
                "tool_name": "get_pr_diff",
                "input": tool_input,
                "output": result
            })
            return result
        
        files = files_response.json()
        
        # Format the output
        result_lines = [
            f"Pull Request #{pr_number}: {pr_data.get('title', 'No title')}",
            f"Author: @{pr_data.get('user', {}).get('login', 'Unknown')}",
            f"Branch: {pr_data.get('head', {}).get('ref', '?')} → {pr_data.get('base', {}).get('ref', '?')}",
            f"Status: {pr_data.get('state', 'unknown').upper()}",
            f"Description: {pr_data.get('body', 'No description provided')}",
            f"\n{'='*80}",
            f"Files Changed: {len(files)}",
            f"{'='*80}\n"
        ]
        
        for file in files:
            filename = file.get("filename", "Unknown")
            status = file.get("status", "modified")
            additions = file.get("additions", 0)
            deletions = file.get("deletions", 0)
            changes = file.get("changes", 0)
            patch = file.get("patch", "")
            
            # Status emoji
            status_emoji = {
                "added": "🆕",
                "removed": "🗑️",
                "modified": "✏️",
                "renamed": "📝"
            }.get(status, "📄")
            
            result_lines.append(f"\n{status_emoji} {filename} ({status})")
            result_lines.append(f"   +{additions} -{deletions} (~{changes} changes)")
            
            if patch:
                result_lines.append(f"\nDiff:")
                result_lines.append("```diff")
                result_lines.append(patch)
                result_lines.append("```")
            else:
                result_lines.append("   (Binary file or no diff available)")
            
            result_lines.append(f"\n{'-'*80}")
        
        result_lines.append(f"\n\nTotal Changes: +{sum(f.get('additions', 0) for f in files)} -{sum(f.get('deletions', 0) for f in files)}")
        
        result = "\n".join(result_lines)
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while fetching PR diff: {str(e)}"
    
    # Track this tool execution (truncate if too long)
    user_ctx.tool_executions.append({
        "tool_name": "get_pr_diff",
        "input": tool_input,
        "output": result[:1000] + "..." if len(result) > 1000 else result
    })
    
    return result
