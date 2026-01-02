import requests
from typing import List, Dict, Any
from agents import RunContextWrapper, function_tool
from schemas import UserContext


def fetch_repo_tree_recursive(owner: str, repo: str, access_token: str, path: str = "") -> List[Dict[str, Any]]:
    """
    Recursively fetch all files and directories in a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        access_token: GitHub access token
        path: Current path in the repository
    
    Returns:
        List of all files with their paths
    """
    all_files = []
    
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            contents = response.json()
            
            if isinstance(contents, list):
                for item in contents:
                    item_type = item.get('type')
                    item_path = item.get('path', '')
                    item_name = item.get('name', '')
                    
                    if item_type == 'file':
                        all_files.append({
                            'name': item_name,
                            'path': item_path,
                            'type': 'file',
                            'size': item.get('size', 0),
                            'download_url': item.get('download_url', '')
                        })
                    elif item_type == 'dir':
                        # Add directory entry
                        all_files.append({
                            'name': item_name,
                            'path': item_path,
                            'type': 'dir'
                        })
                        # Recursively fetch contents of subdirectory
                        subdir_files = fetch_repo_tree_recursive(owner, repo, access_token, item_path)
                        all_files.extend(subdir_files)
        
    except Exception as e:
        # Silently handle errors in recursive fetching
        pass
    
    return all_files


@function_tool
def cache_repo_structure(ctx: RunContextWrapper[UserContext], repo_name: str = None) -> str:
    """
    Cache the complete file structure of a repository (or all user repositories) in the user context.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Optional repository name in 'owner/repo' format. If not provided, caches all user repos.
    
    Returns:
        A message indicating the caching status
    """
    user_ctx = ctx.context
    
    tool_input = {
        "repo_name": repo_name or "all repositories"
    }
    
    try:
        repos_to_cache = []
        
        if repo_name:
            # Cache specific repository
            if "/" in repo_name:
                owner, repo = repo_name.split("/", 1)
            else:
                owner = user_ctx.github_username
                repo = repo_name
            repos_to_cache.append({"owner": owner, "repo": repo, "full_name": f"{owner}/{repo}"})
        else:
            # Fetch all user repositories
            api_url = "https://api.github.com/user/repos"
            response = requests.get(
                api_url,
                headers={
                    "Authorization": f"Bearer {user_ctx.access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                },
                params={"type": "all", "per_page": 100},
                timeout=30
            )
            
            if response.status_code == 200:
                repos = response.json()
                for repo_data in repos:
                    full_name = repo_data.get('full_name', '')
                    if '/' in full_name:
                        owner, repo = full_name.split('/', 1)
                        repos_to_cache.append({
                            "owner": owner,
                            "repo": repo,
                            "full_name": full_name
                        })
        
        # Cache each repository's structure
        cached_count = 0
        for repo_info in repos_to_cache:
            owner = repo_info['owner']
            repo = repo_info['repo']
            full_name = repo_info['full_name']
            
            # Fetch complete file tree
            file_tree = fetch_repo_tree_recursive(owner, repo, user_ctx.access_token)
            
            # Store in cache
            user_ctx.repos_cache[full_name] = {
                'owner': owner,
                'repo': repo,
                'full_name': full_name,
                'file_count': len([f for f in file_tree if f['type'] == 'file']),
                'dir_count': len([f for f in file_tree if f['type'] == 'dir']),
                'files': file_tree,
                'cached_at': user_ctx.timestamp
            }
            cached_count += 1
        
        if repo_name:
            result = f"""Successfully cached repository structure!
- Repository: {repos_to_cache[0]['full_name']}
- Files: {user_ctx.repos_cache[repos_to_cache[0]['full_name']]['file_count']}
- Directories: {user_ctx.repos_cache[repos_to_cache[0]['full_name']]['dir_count']}
- Total items: {len(user_ctx.repos_cache[repos_to_cache[0]['full_name']]['files'])}

The repository structure is now cached and can be quickly accessed."""
        else:
            total_files = sum(cache['file_count'] for cache in user_ctx.repos_cache.values())
            total_dirs = sum(cache['dir_count'] for cache in user_ctx.repos_cache.values())
            result = f"""Successfully cached all repository structures!
- Repositories cached: {cached_count}
- Total files: {total_files}
- Total directories: {total_dirs}

All repository structures are now cached and can be quickly accessed."""
    
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while caching repository structure: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "cache_repo_structure",
        "input": tool_input,
        "output": result
    })
    
    return result
