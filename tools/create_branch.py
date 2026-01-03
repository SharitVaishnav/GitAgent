import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def create_branch(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,
    branch_name: str,
    from_branch: str = "main"
) -> str:
    """
    Create a new branch in a GitHub repository.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo'
        branch_name: Name for the new branch
        from_branch: Source branch to create from (default: "main")
    
    Returns:
        Success message with branch details
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
        "branch_name": branch_name,
        "from_branch": from_branch
    }
    
    try:
        # Step 1: Get the SHA of the source branch
        ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{from_branch}"
        
        ref_response = requests.get(
            ref_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30
        )
        
        if ref_response.status_code != 200:
            result = f"Error: Source branch '{from_branch}' not found in repository '{full_repo_name}'."
        else:
            source_sha = ref_response.json()["object"]["sha"]
            
            # Step 2: Create the new branch
            create_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
            
            payload = {
                "ref": f"refs/heads/{branch_name}",
                "sha": source_sha
            }
            
            create_response = requests.post(
                create_url,
                headers={
                    "Authorization": f"Bearer {user_ctx.access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                },
                json=payload,
                timeout=30
            )
            
            if create_response.status_code == 201:
                result = f"""Successfully created branch!
- Branch: {branch_name}
- Repository: {full_repo_name}
- Created from: {from_branch}
- SHA: {source_sha[:7]}
- URL: https://github.com/{owner}/{repo}/tree/{branch_name}

You can now work on this branch locally:
  git fetch origin
  git checkout {branch_name}"""
            
            elif create_response.status_code == 422:
                result = f"Error: Branch '{branch_name}' already exists in repository '{full_repo_name}'."
            
            else:
                error_msg = create_response.json().get("message", "Unknown error")
                result = f"Error creating branch: {error_msg} (Status: {create_response.status_code})"
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while creating branch: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "create_branch",
        "input": tool_input,
        "output": result[:500] if len(result) > 500 else result
    })
    
    return result
