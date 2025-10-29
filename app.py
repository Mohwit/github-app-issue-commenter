import os
import hmac
import hashlib
import jwt
import time
from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional
from github import Github, GithubIntegration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="GitHub Issue Commenter Bot")

# GitHub App Configuration
APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY", "").replace("\\n", "\n")
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

# PR Guidelines template
PR_GUIDELINES = """
👋 **Thank you for creating this issue!**

If you'd like to submit a Pull Request to address this issue, please follow these guidelines:

## PR Guidelines

### Before Creating a PR
- 🔍 Search existing PRs to avoid duplicates
- 💬 Comment on this issue that you're working on it
- 🌿 Create a new branch from `main`

### PR Requirements
- ✅ Write clear, descriptive commit messages
- ✅ Include tests for new features or bug fixes
- ✅ Update documentation if needed
- ✅ Ensure all tests pass
- ✅ Follow the existing code style

### PR Description Should Include
- 📝 Summary of changes
- 🔗 Reference to this issue (e.g., "Fixes #123")
- 🧪 How to test the changes
- 📸 Screenshots (if applicable)

### Review Process
- ⏱️ PRs are typically reviewed within 2-3 business days
- 🔄 Address review comments promptly
- ✨ Squash commits before merging (if requested)

**Happy coding! 🚀**
"""


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that the payload was sent from GitHub by validating SHA256."""
    if not WEBHOOK_SECRET:
        raise ValueError("GITHUB_WEBHOOK_SECRET not configured")
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


def get_jwt_token() -> str:
    """Generate a JWT token for GitHub App authentication."""
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + (10 * 60),  # JWT expires in 10 minutes
        'iss': APP_ID
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm='RS256')


def get_installation_access_token(installation_id: int) -> str:
    """Get an installation access token for the GitHub App."""
    jwt_token = get_jwt_token()
    integration = GithubIntegration(APP_ID, PRIVATE_KEY)
    auth = integration.get_access_token(installation_id)
    return auth.token


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": "GitHub Issue Commenter Bot",
        "message": "Server is running"
    }


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.post("/webhook")
async def webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """Handle GitHub webhook events."""
    
    # Read the request body
    payload_body = await request.body()
    
    # Verify the webhook signature
    if not x_hub_signature_256:
        raise HTTPException(status_code=403, detail="Missing signature header")
    
    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse the JSON payload
    payload = await request.json()
    
    # Handle only "issues" events
    if x_github_event == "issues":
        action = payload.get("action")
        
        # Only respond to newly opened issues
        if action == "opened":
            issue = payload.get("issue")
            repository = payload.get("repository")
            installation = payload.get("installation")
            
            if not all([issue, repository, installation]):
                return {"status": "skipped", "reason": "Missing required data"}
            
            installation_id = installation.get("id")
            issue_number = issue.get("number")
            repo_full_name = repository.get("full_name")
            
            try:
                # Get installation access token
                access_token = get_installation_access_token(installation_id)
                
                # Create GitHub client
                g = Github(access_token)
                repo = g.get_repo(repo_full_name)
                issue_obj = repo.get_issue(issue_number)
                
                # Post the comment
                issue_obj.create_comment(PR_GUIDELINES)
                
                return {
                    "status": "success",
                    "message": f"Comment posted on issue #{issue_number}",
                    "repository": repo_full_name
                }
            
            except Exception as e:
                print(f"Error posting comment: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    # For other events, just acknowledge
    return {"status": "ok", "event": x_github_event}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

