# Quick Setup Guide for GitHub App

## Complete Step-by-Step Tutorial

### Part 1: Setting Up Your Development Environment

#### 1.1 Install Dependencies

```bash
cd /Users/msingh/Desktop/github-app-issue-commenter
pip install -r requirements.txt
```

#### 1.2 Set Up ngrok (for local testing)

```bash
# Download from https://ngrok.com/download
# Or install via homebrew on Mac:
brew install ngrok

# Start ngrok
ngrok http 8000
```

Keep this terminal open and note the HTTPS URL (e.g., `https://abc123.ngrok.io`)

---

### Part 2: Creating Your GitHub App

#### 2.1 Navigate to GitHub Apps

- **Personal Account**: https://github.com/settings/apps
- **Organization**: https://github.com/organizations/YOUR_ORG/settings/apps

#### 2.2 Click "New GitHub App"

#### 2.3 Fill Out the Registration Form

**Basic Information:**

- **GitHub App name**: `Issue PR Guidelines Bot` (must be globally unique)
- **Homepage URL**: `https://github.com/YOUR_USERNAME`
- **Webhook URL**: `https://YOUR_NGROK_URL.ngrok.io/webhook`
  - Example: `https://abc123.ngrok.io/webhook`

**Webhook Secret:**
Generate a secret:

```bash
# Run this in terminal to generate a random secret:
openssl rand -hex 20
```

Copy the output and paste it in the "Webhook secret" field.
**SAVE THIS SECRET** - you'll need it for your `.env` file!

**Permissions:**

Under "Repository permissions":

- **Issues**: Select "Read and write"

Under "Subscribe to events":

- Check ✅ **Issues**

**Where can this GitHub App be installed?**

- Select "Any account" (or "Only on this account" if you prefer)

#### 2.4 Click "Create GitHub App" ✅

#### 2.5 Save Your App Credentials

After creation, you'll see your app's page:

1. **App ID**: Note the number at the top (e.g., 123456)

2. **Private Key**:
   - Scroll down to "Private keys" section
   - Click "Generate a private key"
   - A `.pem` file will download
   - **Keep this file safe!**

---

### Part 3: Configuring the Application

#### 3.1 Create Your `.env` File

```bash
cd /Users/msingh/Desktop/github-app-issue-commenter
cp .env.example .env
```

#### 3.2 Edit the `.env` File

Open `.env` in your text editor and fill in:

```env
GITHUB_APP_ID=123456
GITHUB_WEBHOOK_SECRET=your_secret_from_step_2.3
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(paste entire contents of the .pem file here)
...
-----END RSA PRIVATE KEY-----"
```

**Tips:**

- For GITHUB_APP_ID: Use the number from step 2.5.1
- For GITHUB_WEBHOOK_SECRET: Use the secret you generated in step 2.3
- For GITHUB_PRIVATE_KEY: Open the `.pem` file and copy everything, including the BEGIN and END lines

---

### Part 4: Running the App

#### 4.1 Start Your FastAPI Server

```bash
python app.py
```

You should see:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 4.2 Test the Health Endpoint

In another terminal:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{ "status": "healthy" }
```

---

### Part 5: Installing the App on a Repository

#### 5.1 Go to Your GitHub App Settings

Navigate back to: https://github.com/settings/apps

Click on your app name.

#### 5.2 Install the App

1. Click "Install App" in the left sidebar
2. Choose your account/organization
3. Select:
   - **All repositories** (if you want it everywhere), OR
   - **Only select repositories** (choose specific repos)
4. Click "Install"

---

### Part 6: Testing the Bot!

#### 6.1 Create a Test Issue

1. Go to one of your repositories where the app is installed
2. Click "Issues" tab
3. Click "New issue"
4. Add a title and description
5. Click "Submit new issue"

#### 6.2 Watch for the Comment

Within 1-2 seconds, your bot should automatically post a comment with PR guidelines! 🎉

#### 6.3 Verify in Logs

Check your terminal where `python app.py` is running. You should see the webhook request being processed.

#### 6.4 Check Webhook Delivery (if issues occur)

1. Go to GitHub App settings
2. Click "Advanced" tab
3. Scroll to "Recent Deliveries"
4. Click on the latest delivery to see:
   - Request payload
   - Response from your server
   - Any errors

---

### Part 7: Deploying to Production

Once everything works locally, deploy to a cloud platform:

#### Option A: Railway (Easiest)

1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect this repository
4. Add environment variables (GITHUB_APP_ID, GITHUB_WEBHOOK_SECRET, GITHUB_PRIVATE_KEY)
5. Deploy
6. Copy the Railway URL
7. Update GitHub App webhook URL to: `https://your-app.railway.app/webhook`

#### Option B: Render

1. Sign up at https://render.com
2. New → "Web Service"
3. Connect GitHub repository
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy
8. Update webhook URL in GitHub App settings

#### Option C: Your Own Server

```bash
# On your server
git clone YOUR_REPO_URL
cd github-app-issue-commenter
pip install -r requirements.txt

# Set environment variables
export GITHUB_APP_ID=123456
export GITHUB_WEBHOOK_SECRET=your_secret
export GITHUB_PRIVATE_KEY="your_key"

# Run with nohup or systemd
nohup python app.py &
```

---

## 🎊 Congratulations!

You've successfully created and deployed a GitHub App!

Your app will now automatically comment on every new issue with PR guidelines.

---

## Common Issues & Solutions

### Issue 1: "Invalid signature"

**Cause**: Webhook secret mismatch
**Fix**: Ensure the secret in `.env` matches the one in GitHub App settings

### Issue 2: Bot doesn't comment

**Checklist**:

- [ ] Server is running (`python app.py`)
- [ ] ngrok is running (for local testing)
- [ ] Webhook URL is correct in GitHub App settings
- [ ] App is installed on the repository
- [ ] App has "Issues: Read & Write" permission
- [ ] "Issues" event is subscribed

### Issue 3: Authentication error

**Cause**: Private key issue
**Fix**:

- Ensure the entire private key is copied correctly
- Include BEGIN and END lines
- No extra spaces or line breaks outside the key

---

## Next Steps

Now that you have a working GitHub App, you can:

1. **Customize the PR guidelines** - Edit `PR_GUIDELINES` in `app.py`
2. **Add more features** - Comment on PRs, check code quality, etc.
3. **Store custom guidelines per repo** - Use a database or config files
4. **Add more events** - Respond to PR opens, comments, etc.

Happy coding! 🚀
