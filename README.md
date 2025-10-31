# GitHub App: Issue Commenter Bot 🤖

A GitHub App built with Python and FastAPI that automatically comments on newly created issues with PR guidelines for your repository.

## 📋 What This App Does

When someone creates a new issue in your repository, this bot automatically:

- Detects the new issue via GitHub webhooks
- Posts a friendly comment with PR guidelines
- Helps contributors understand how to submit quality pull requests
- **NEW!** 🎨 View all issues in a beautiful web dashboard

## 🏗️ Architecture

- **Framework**: FastAPI (Python)
- **GitHub Integration**: PyGithub + PyJWT
- **Authentication**: GitHub App with webhook validation
- **UI**: Beautiful web dashboard with real-time updates
- **Deployment**: Can be deployed to any platform (Railway, Render, Heroku, etc.)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A GitHub account
- A public URL for webhooks (for local development, use ngrok or similar)

### Step 1: Clone and Install Dependencies

```bash
# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create a GitHub App

1. **Go to GitHub Settings**:

   - For personal account: `https://github.com/settings/apps`
   - For organization: `https://github.com/organizations/YOUR_ORG/settings/apps`

2. **Click "New GitHub App"**

3. **Fill in the form**:

   - **GitHub App name**: `Issue Commenter Bot` (or any unique name)
   - **Homepage URL**: `https://github.com/YOUR_USERNAME` (or your app URL)
   - **Webhook URL**: Your server URL + `/webhook`
     - For local testing with ngrok: `https://YOUR_NGROK_ID.ngrok.io/webhook`
     - For production: `https://your-domain.com/webhook`
   - **Webhook secret**: Generate a random string (you can use: `openssl rand -hex 20`)
     - Save this! You'll need it for the `.env` file

4. **Set Permissions**:

   - Repository permissions:
     - **Issues**: Read & Write (to read issue events and post comments)
   - Subscribe to events:
     - ✅ Check **Issues**

5. **Create the App**

6. **After Creation**:
   - Note down the **App ID** (you'll see it at the top)
   - Scroll down to **Private keys** section
   - Click **Generate a private key**
   - A `.pem` file will download - save it securely!

### Step 3: Configure Environment Variables

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

2. Edit `.env` with your values:

```env
GITHUB_APP_ID=123456
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(paste your entire private key here)
...
-----END RSA PRIVATE KEY-----"
```

**Important**:

- The private key should be in quotes and use `\n` for newlines, OR
- You can copy the entire key as-is between the quotes (the app handles both formats)

### Step 4: Run the Application

#### For Local Development

```bash
# Run the FastAPI server
python app.py
```

The server will start at `http://localhost:8000`

#### For Local Testing with ngrok

In a separate terminal:

```bash
# Install ngrok if you haven't: https://ngrok.com/download
ngrok http 8000
```

Copy the `https://` URL from ngrok and:

1. Go back to your GitHub App settings
2. Update the **Webhook URL** to `https://YOUR_NGROK_ID.ngrok.io/webhook`
3. Save changes

### Step 5: Install the App on a Repository

1. Go to your GitHub App settings page
2. Click on **Install App** in the left sidebar
3. Choose the account/organization
4. Select **Only select repositories** or **All repositories**
5. Click **Install**

### Step 6: Test It!

1. Go to one of your repositories where the app is installed
2. Create a new issue
3. Within seconds, you should see a comment from your bot with PR guidelines! 🎉
4. **View the Dashboard**: Open `http://localhost:8000` in your browser to see the issue appear!

## 🎨 Web Dashboard

Your app includes a beautiful web dashboard to monitor all new issues in real-time!

### Features

- 📊 **Real-Time Monitoring** - See all new issues as they're created
- 🔍 **Search & Filter** - Find issues by title, repo, or user
- 📅 **Time Filters** - View today's issues, this week, or all
- 📈 **Statistics** - Track total issues and active repositories
- 🎯 **Direct Links** - Click to view issues on GitHub
- 📱 **Responsive Design** - Works on mobile, tablet, and desktop

### Accessing the Dashboard

**Local Development:**
```
http://localhost:8000
```

**Production:**
```
https://your-app.railway.app
https://your-app.onrender.com
https://your-app.fly.dev
```

### Dashboard API

Get issues programmatically:
```bash
curl https://your-app.com/api/issues
```

**Note**: Issues are stored in-memory (last 100 issues). For persistent storage, see [UI_GUIDE.md](UI_GUIDE.md).

For more details, see [UI_GUIDE.md](UI_GUIDE.md).

## 🔧 Customization

### Modify the PR Guidelines

Edit the `PR_GUIDELINES` variable in `app.py` to customize the message:

```python
PR_GUIDELINES = """
Your custom guidelines here...
"""
```

### Change the Comment Trigger

Currently, the app comments on all new issues. You can modify the logic in the webhook handler to:

- Only comment on issues with specific labels
- Only comment on issues that match certain criteria
- Comment on other events (PR opened, etc.)

Example - only comment if issue has "help wanted" label:

```python
if action == "opened":
    labels = [label["name"] for label in issue.get("labels", [])]
    if "help wanted" not in labels:
        return {"status": "skipped", "reason": "No help wanted label"}
    # ... rest of the code
```

## 🌐 Deployment

### Deploy to Railway (Recommended for beginners)

1. Go to [Railway.app](https://railway.app/)
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Add environment variables in Railway dashboard
6. Railway will auto-deploy and give you a URL
7. Update your GitHub App webhook URL to `https://your-app.railway.app/webhook`

### Deploy to Render

1. Go to [Render.com](https://render.com/)
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy and update webhook URL

### Deploy to Heroku

```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set GITHUB_APP_ID=your_app_id
heroku config:set GITHUB_WEBHOOK_SECRET=your_secret
heroku config:set GITHUB_PRIVATE_KEY="your_private_key"
git push heroku main
```

Don't forget to add a `Procfile`:

```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

## 🔍 Monitoring and Debugging

### Check if the server is running

```bash
curl http://localhost:8000/health
```

### View logs

```bash
# The app prints logs to console
# Check the terminal where you ran `python app.py`
```

### Webhook Delivery

1. Go to your GitHub App settings
2. Click on **Advanced** tab
3. Scroll to **Recent Deliveries**
4. Click on any delivery to see:
   - Request headers and payload
   - Response from your server
   - Any errors

## 🛡️ Security Best Practices

1. **Never commit `.env` or private keys to git**

   - Already included in `.gitignore`

2. **Use webhook secrets**

   - Always validate webhook signatures (already implemented)

3. **Restrict permissions**

   - Only request minimum required permissions

4. **Rotate keys periodically**

   - Generate new private keys in GitHub App settings

5. **Use environment variables**
   - Never hardcode secrets in code

## 📚 API Endpoints

| Endpoint      | Method | Description                        |
| ------------- | ------ | ---------------------------------- |
| `/`           | GET    | **Web Dashboard** - View all issues|
| `/health`     | GET    | Health check for monitoring        |
| `/api/issues` | GET    | Get all issues as JSON             |
| `/webhook`    | POST   | Receives GitHub webhook events     |

## 🐛 Troubleshooting

### Issue: "Invalid signature"

**Solution**: Make sure your `GITHUB_WEBHOOK_SECRET` in `.env` matches exactly what you set in the GitHub App settings.

### Issue: "Missing signature header"

**Solution**: Ensure you're sending requests to `/webhook` with proper GitHub webhook headers. For testing, use the GitHub webhook "Recent Deliveries" to redeliver events.

### Issue: Bot doesn't comment

**Checklist**:

1. ✅ App is installed on the repository
2. ✅ Webhook URL is correct and accessible
3. ✅ Server is running
4. ✅ Environment variables are set correctly
5. ✅ GitHub App has "Issues: Read & Write" permission
6. ✅ "Issues" event is subscribed in the app settings

Check webhook delivery logs in GitHub App settings for errors.

### Issue: Authentication errors

**Solution**:

- Verify your `GITHUB_APP_ID` is correct
- Ensure private key is properly formatted in `.env`
- Check that the private key matches the one generated in GitHub App settings

## 🎯 Next Steps

Once you have the basic app working, you can extend it to:

- 💾 Store custom guidelines per repository in a database
- 🏷️ Add different templates based on issue labels
- 📊 Track metrics (how many PRs were submitted after the comment)
- 🌍 Support multiple languages
- 📝 Allow repository admins to customize guidelines via config file
- 🤝 Integrate with other tools (Slack notifications, etc.)

## 📖 Learn More

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)

## 📄 License

See LICENSE file.

## 🤝 Contributing

Feel free to submit issues and pull requests!

---

**Happy automating! 🎉**
