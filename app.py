import os
import hmac
import hashlib
import jwt
import time
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict
from github import Github, GithubIntegration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="GitHub Issue Commenter Bot")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for issues (in production, use a database)
recent_issues: List[Dict] = []
MAX_STORED_ISSUES = 100

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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Dashboard - shows all recent issues."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_issues": len(recent_issues),
        "app_name": "GitHub Issue Commenter Bot"
    })


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/api/issues")
async def get_issues():
    """API endpoint to get all recent issues."""
    return {
        "total": len(recent_issues),
        "issues": recent_issues
    }


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
                
                # Store issue data for dashboard
                # Handle None body (issues without description)
                issue_body = issue.get("body") or ""
                truncated_body = issue_body[:200] + "..." if len(issue_body) > 200 else issue_body
                
                issue_data = {
                    "number": issue_number,
                    "title": issue.get("title"),
                    "body": truncated_body,
                    "repository": repo_full_name,
                    "user": issue.get("user", {}).get("login"),
                    "user_avatar": issue.get("user", {}).get("avatar_url"),
                    "url": issue.get("html_url"),
                    "created_at": issue.get("created_at"),
                    "timestamp": datetime.now().isoformat(),
                    "labels": [label.get("name") for label in issue.get("labels", [])]
                }
                
                # Add to recent issues (keep only last MAX_STORED_ISSUES)
                recent_issues.insert(0, issue_data)
                if len(recent_issues) > MAX_STORED_ISSUES:
                    recent_issues.pop()
                
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

