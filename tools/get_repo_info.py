import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def get_repo_info(ctx: RunContextWrapper[UserContext], repo_name: str) -> dict:
    """
    Get repository information including fork status and parent repo.
    
    Args:
        ctx: User context with access token
        repo_name: Repository name (owner/repo or just repo)
    
    Returns:
        Dictionary with repo info including fork status and parent
    """
    user_ctx = ctx.context
    
    # Parse repository name
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
    else:
        owner = user_ctx.github_username
        repo = repo_name
    
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            repo_info = {
                "full_name": data.get("full_name"),
                "is_fork": data.get("fork", False),
                "parent": None,
                "source": None
            }
            
            if repo_info["is_fork"]:
                parent = data.get("parent", {})
                source = data.get("source", {})
                
                repo_info["parent"] = {
                    "full_name": parent.get("full_name"),
                    "owner": parent.get("owner", {}).get("login"),
                    "name": parent.get("name"),
                    "url": parent.get("html_url")
                }
                
                repo_info["source"] = {
                    "full_name": source.get("full_name"),
                    "owner": source.get("owner", {}).get("login"),
                    "name": source.get("name")
                }
            
            return repo_info
        else:
            return {"error": f"Repository not found: {owner}/{repo}"}
    
    except Exception as e:
        return {"error": str(e)}
