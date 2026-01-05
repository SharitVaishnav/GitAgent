# PR Review Agent

An intelligent GitHub Pull Request review agent that analyzes code changes and provides automated code reviews.

## Overview

The PR Review Agent is a specialized AI agent that:
- Fetches pull request diffs and file changes
- Analyzes code quality, security, and best practices
- Provides constructive feedback
- Submits reviews (approve, request changes, or comment)

## Architecture

### Components

1. **`get_pr_diff.py`** - Tool to fetch PR details and diffs
2. **`review_pull_request.py`** - Tool to submit PR reviews
3. **`pr_review_agent.py`** - Agent that orchestrates the review process
4. **`config.py`** - Main agent configuration (updated)

### Flow

```
User Request → Main Agent → PR Review Agent → get_pr_diff → Analyze Code → review_pull_request → Submit Review
```

## Features

### Code Analysis

The agent reviews code for:
- ✅ **Code Quality**: Best practices, consistency, style
- 🐛 **Bugs**: Potential logic errors and edge cases
- 🔒 **Security**: Security vulnerabilities and risks
- ⚡ **Performance**: Performance implications
- 📝 **Documentation**: Comments and documentation quality
- 🧪 **Testing**: Test coverage and quality
- 🏗️ **Architecture**: Design patterns and structure
- 📛 **Naming**: Variable and function naming conventions

### Review Actions

The agent can:
1. **APPROVE** - Code is good quality with no significant issues
2. **REQUEST_CHANGES** - Bugs, security issues, or improvements needed
3. **COMMENT** - Suggestions without blocking merge

## Usage

### Basic Review

```
User: "Review PR #42 in my-repo"
```

The agent will:
1. Fetch the PR diff
2. Analyze all changed files
3. Provide detailed feedback
4. Submit an appropriate review

### Review Specific Repository

```
User: "Review pull request #15 in owner/repository"
```

### Example Interaction

**User**: "Can you review PR #7 in GitAgent?"

**Agent**: 
1. Fetches PR #7 details and diffs
2. Analyzes the code changes
3. Provides feedback like:

```
## Summary
This PR adds authentication middleware to the API. Overall good implementation 
with a few suggestions for improvement.

## Strengths
- Clean separation of concerns
- Proper error handling for invalid tokens
- Good test coverage

## Issues Found
- Missing rate limiting on auth endpoint (security concern)
- Token expiration not validated
- No logging for failed authentication attempts

## Suggestions
- Consider adding rate limiting using a library like `slowapi`
- Validate token expiration time
- Add structured logging for security events

## Conclusion
Requesting changes due to security concerns. Once addressed, this will be 
ready to merge.
```

4. Submits review as "REQUEST_CHANGES"

## API Reference

### get_pr_diff

Fetches PR details and file diffs.

```python
get_pr_diff(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,  # "owner/repo" or just "repo"
    pr_number: int   # PR number
) -> str
```

**Returns**: Formatted diff with:
- PR metadata (title, author, branch, status)
- List of changed files
- Additions/deletions per file
- Full diff patches

### review_pull_request

Submits a review for a PR.

```python
review_pull_request(
    ctx: RunContextWrapper[UserContext],
    repo_name: str,     # "owner/repo" or just "repo"
    pr_number: int,     # PR number
    event: str,         # "APPROVE", "REQUEST_CHANGES", or "COMMENT"
    body: str = ""      # Review feedback
) -> str
```

**Events**:
- `APPROVE` - Approve the PR
- `REQUEST_CHANGES` - Request changes (requires body)
- `COMMENT` - Add comment without approval/rejection

## Integration

The PR Review Agent is integrated into the main agent system via `config.py`:

```python
from pr_review_agent import create_pr_review_agent

pr_review_agent = create_pr_review_agent()

agent = Agent[UserContext](
    tools=[
        # ... other tools
        pr_review_agent.as_tool(
            tool_name="pr_review_agent",
            tool_description="Use this agent to review pull requests..."
        )
    ]
)
```

## Permissions

The user must have:
- Read access to the repository
- Write access to submit reviews
- Cannot review their own PRs (GitHub limitation)

## Error Handling

The agent handles:
- ❌ PR not found
- ❌ Insufficient permissions
- ❌ Already reviewed
- ❌ Author trying to review own PR
- ❌ Network errors

## Future Enhancements

Potential improvements:
- [ ] Line-by-line comments on specific code sections
- [ ] Integration with linters and static analysis tools
- [ ] Custom review templates
- [ ] Review history tracking
- [ ] Automated review based on repository rules
- [ ] Support for review threads and discussions

## Example Use Cases

### 1. Quick Review
```
User: "Review the latest PR in my-app"
```

### 2. Detailed Analysis
```
User: "Can you do a thorough security review of PR #23?"
```

### 3. Multiple PRs
```
User: "Review all open PRs in my-repo and approve the ones that look good"
```

## Testing

To test the PR review agent:

1. Create a test PR in a repository
2. Ask the agent to review it
3. Check the PR on GitHub for the review

Example:
```bash
# Create a test branch and PR first
git checkout -b test-pr-review
# Make some changes
git commit -am "Test changes"
git push origin test-pr-review
# Create PR on GitHub

# Then ask the agent
"Review PR #1 in test-repo"
```

## Troubleshooting

### Review Not Submitted
- Check if you're the PR author (can't review own PRs)
- Verify you have write access to the repository
- Ensure the PR is still open

### Missing Diffs
- Large PRs may have truncated diffs
- Binary files won't show diffs
- Check GitHub API rate limits

### Permission Errors
- Verify your GitHub token has `repo` scope
- Check repository access settings
- Ensure you're not blocked from the repository

## Related Tools

- `list_pull_requests` - List PRs in a repository
- `merge_pull_request` - Merge a PR
- `create_pull_request` - Create a new PR
- `get_file_content` - View specific file contents
