import requests
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def list_repo_files(ctx: RunContextWrapper[UserContext], repo_name: str, path: str = "") -> str:
    """
    List all files and directories in a GitHub repository.
    Validates repo name against cached repositories and suggests alternatives if not found.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo' (uses authenticated user)
        path: Optional path within the repository (default: root directory)
    
    Returns:
        A formatted list of files and directories in the repository
    """
    user_ctx = ctx.context
    
    # Parse repository name
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
        full_repo_name = f"{owner}/{repo}"
    else:
        owner = user_ctx.github_username
        repo = repo_name
        full_repo_name = f"{owner}/{repo}"
    
    # Prepare input (what the tool received)
    tool_input = {
        "repo_name": full_repo_name,
        "path": path or "root"
    }
    
    try:
        # Step 1: Check if repos are cached
        if user_ctx.repos_cache:
            # Step 2: Validate if the repository exists in cached repos
            if full_repo_name not in user_ctx.repos_cache:
                cached_repo_names = list(user_ctx.repos_cache.keys())
                
                result = f"""❌ Repository '{full_repo_name}' not found in cached repositories.

You have {len(cached_repo_names)} cached repositories:
"""
                for idx, cached_repo in enumerate(cached_repo_names, 1):
                    result += f"{idx}. {cached_repo}\n"
                
                # Track this tool execution
                user_ctx.tool_executions.append({
                    "tool_name": "list_repo_files",
                    "input": tool_input,
                    "output": result
                })
                
                return result
        
        # Step 3: Proceed with listing files via GitHub API
        # GitHub API endpoint for repository contents
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        # Make the API request
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {user_ctx.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            contents = response.json()
            
            # Handle single file response
            if isinstance(contents, dict):
                result = f"""File: {contents.get('name', 'Unknown')}
- Type: {contents.get('type', 'file')}
- Size: {contents.get('size', 0)} bytes
- Path: {contents.get('path', '')}
- Download URL: {contents.get('download_url', 'N/A')}"""
            
            # Handle directory listing
            elif isinstance(contents, list):
                if not contents:
                    result = f"The directory '{path or 'root'}' in {owner}/{repo} is empty."
                else:
                    # Separate files and directories
                    directories = [item for item in contents if item.get('type') == 'dir']
                    files = [item for item in contents if item.get('type') == 'file']
                    
                    result_lines = [f"Contents of '{path or 'root'}' in {owner}/{repo}:\n"]
                    
                    # List directories first
                    if directories:
                        result_lines.append("📁 Directories:")
                        for item in directories:
                            name = item.get('name', 'Unknown')
                            result_lines.append(f"  - {name}/")
                    
                    # Then list files
                    if files:
                        result_lines.append("\n📄 Files:")
                        for item in files:
                            name = item.get('name', 'Unknown')
                            size = item.get('size', 0)
                            # Format size
                            if size < 1024:
                                size_str = f"{size} B"
                            elif size < 1024 * 1024:
                                size_str = f"{size / 1024:.1f} KB"
                            else:
                                size_str = f"{size / (1024 * 1024):.1f} MB"
                            result_lines.append(f"  - {name} ({size_str})")
                    
                    result_lines.append(f"\nTotal: {len(directories)} directories, {len(files)} files")
                    result = "\n".join(result_lines)
            else:
                result = "Unexpected response format from GitHub API"
                
        elif response.status_code == 404:
            result = f"Error: Repository '{owner}/{repo}' or path '{path}' not found."
            
        elif response.status_code == 403:
            result = f"Error: You don't have permission to access '{owner}/{repo}'. The repository might be private."
            
        elif response.status_code == 401:
            result = "Error: Authentication failed. Please check your access token."
            
        else:
            error_msg = response.json().get("message", "Unknown error") if response.text else "Unknown error"
            result = f"Error listing repository contents: {error_msg} (Status: {response.status_code})"
    
    except ValueError as e:
        result = f"Error: Invalid repository name format. {str(e)}"
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while listing repository files: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "list_repo_files",
        "input": tool_input,
        "output": result
    })
    
    return result
