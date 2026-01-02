import requests
import base64
from agents import RunContextWrapper, function_tool
from schemas import UserContext


@function_tool
def get_file_content(ctx: RunContextWrapper[UserContext], repo_name: str, file_path: str) -> str:
    """
    Fetch the content of a specific file from a GitHub repository.
    
    Args:
        ctx: The run context wrapper containing user context
        repo_name: Repository name in 'owner/repo' format or just 'repo' (uses authenticated user)
        file_path: Path to the file within the repository
    
    Returns:
        The content of the file or an error message
    """
    user_ctx = ctx.context
    
    # Parse repository name
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
    else:
        owner = user_ctx.github_username
        repo = repo_name
    
    # Prepare input (what the tool received)
    tool_input = {
        "repo_name": f"{owner}/{repo}",
        "file_path": file_path
    }
    
    try:
        # GitHub API endpoint for file contents
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        
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
            file_data = response.json()
            
            # Check if it's a file (not a directory)
            if file_data.get('type') != 'file':
                result = f"Error: '{file_path}' is not a file. It appears to be a {file_data.get('type', 'directory')}."
            else:
                # Get file metadata
                file_name = file_data.get('name', 'Unknown')
                file_size = file_data.get('size', 0)
                encoding = file_data.get('encoding', 'base64')
                
                # Format size
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                
                # Decode content
                if encoding == 'base64':
                    content_encoded = file_data.get('content', '')
                    try:
                        # Remove whitespace and decode
                        content_bytes = base64.b64decode(content_encoded)
                        # Try to decode as UTF-8 text
                        try:
                            content = content_bytes.decode('utf-8')
                            
                            # Limit content length for very large files
                            max_length = 10000  # characters
                            if len(content) > max_length:
                                content = content[:max_length] + f"\n\n... (truncated, showing first {max_length} characters of {len(content)} total)"
                            
                            result = f"""File: {file_name}
Path: {file_path}
Size: {size_str}
Repository: {owner}/{repo}

--- Content ---
{content}"""
                        except UnicodeDecodeError:
                            # Binary file
                            result = f"""File: {file_name}
Path: {file_path}
Size: {size_str}
Repository: {owner}/{repo}
Type: Binary file

This is a binary file and cannot be displayed as text.
Download URL: {file_data.get('download_url', 'N/A')}"""
                    except Exception as e:
                        result = f"Error decoding file content: {str(e)}"
                else:
                    result = f"Error: Unsupported encoding '{encoding}'"
                
        elif response.status_code == 404:
            # File not found - check if repository is cached
            full_repo_name = f"{owner}/{repo}"
            
            if full_repo_name in user_ctx.repos_cache:
                # Get all file paths from cache
                cached_files = user_ctx.repos_cache[full_repo_name]['files']
                all_file_paths = [f['path'] for f in cached_files if f['type'] == 'file']
                
                result = f"""Error: File '{file_path}' not found in repository '{full_repo_name}'. Available files in this repository: {chr(10).join(f"  - {path}" for path in sorted(all_file_paths))} Please choose the closest matching file from the list above and try again."""
            else:
                result = f"Error: File '{file_path}' not found in repository '{owner}/{repo}'.1"

            
        elif response.status_code == 403:
            result = f"Error: You don't have permission to access '{owner}/{repo}'. The repository might be private."
            
        elif response.status_code == 401:
            result = "Error: Authentication failed. Please check your access token."
            
        else:
            error_msg = response.json().get("message", "Unknown error") if response.text else "Unknown error"
            result = f"Error fetching file content: {error_msg} (Status: {response.status_code})"
    
    except ValueError as e:
        result = f"Error: Invalid repository name format. {str(e)}"
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        result = f"Unexpected error while fetching file content: {str(e)}"
    
    # Track this tool execution
    user_ctx.tool_executions.append({
        "tool_name": "get_file_content",
        "input": tool_input,
        "output": result[:500] + "..." if len(result) > 500 else result  # Truncate for tracking
    })
    
    return result
