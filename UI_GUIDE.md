# 📊 Dashboard UI Guide

Your GitHub App now has a beautiful web dashboard to monitor all new issues!

## 🎨 Features

### 1. **Real-Time Issue Monitoring**

- See all new issues as they're created
- Auto-refreshes every 30 seconds
- Manual refresh button available

### 2. **Rich Issue Details**

Each issue card shows:

- 👤 User who created it (with avatar)
- 📝 Issue title and description
- 📦 Repository name
- 🏷️ Labels
- ⏰ Time created
- 🔗 Direct link to GitHub

### 3. **Search & Filter**

- 🔍 **Search**: Find issues by title, repository, or username
- 📅 **Filters**:
  - All issues
  - Today's issues
  - This week's issues

### 4. **Statistics**

- Total issues processed
- Number of active repositories

## 🚀 Accessing the Dashboard

### Local Development

```bash
# Start your app
python app.py

# Open in browser
http://localhost:8000
```

### Production

Once deployed, your dashboard will be at:

```
https://your-app-domain.com/
```

**Examples**:

- Railway: `https://your-app.up.railway.app`
- Render: `https://your-app.onrender.com`
- Fly.io: `https://your-app.fly.dev`

## 🎯 How It Works

### Data Storage

Issues are stored **in-memory** (RAM) on your server:

- Stores up to 100 most recent issues
- Data persists as long as the server is running
- **Limitation**: Data is lost when server restarts

### API Endpoint

The dashboard fetches data from:

```
GET /api/issues
```

**Response**:

```json
{
  "total": 5,
  "issues": [
    {
      "number": 42,
      "title": "Bug in login",
      "body": "When I try to login...",
      "repository": "octocat/Hello-World",
      "user": "johndoe",
      "user_avatar": "https://...",
      "url": "https://github.com/...",
      "created_at": "2024-01-15T10:30:00Z",
      "timestamp": "2024-01-15T10:30:00Z",
      "labels": ["bug", "high-priority"]
    }
  ]
}
```

## 🔧 Customization

### Change the Number of Stored Issues

In `app.py`, modify:

```python
MAX_STORED_ISSUES = 100  # Change to your preferred number
```

### Customize the UI Colors

Edit `static/style.css`:

```css
/* Change the gradient colors */
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Change the primary color */
.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Add More Statistics

In `templates/dashboard.html`, add more stat cards:

```html
<div class="stat-card">
  <div class="stat-number" id="your-stat">0</div>
  <div class="stat-label">Your Label</div>
</div>
```

## 📈 Upgrading to Persistent Storage

For production use, you might want to store issues permanently using a database.

### Option A: SQLite (Simple)

```bash
# Install SQLAlchemy
pip install sqlalchemy
```

Create a simple database model:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Issue(Base):
    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    title = Column(String)
    repository = Column(String)
    user = Column(String)
    url = Column(String)
    created_at = Column(DateTime)

engine = create_engine('sqlite:///issues.db')
Base.metadata.create_all(engine)
```

### Option B: PostgreSQL (Production-Ready)

Most hosting platforms offer free PostgreSQL:

```bash
# Install psycopg2
pip install psycopg2-binary

# Use PostgreSQL URL
DATABASE_URL = "postgresql://user:password@host:5432/database"
```

### Option C: MongoDB (NoSQL)

```bash
pip install motor pymongo
```

## 🎨 UI Screenshots Description

### Main Dashboard

- Clean, modern gradient background (purple to pink)
- White cards with subtle shadows
- Responsive design (works on mobile!)

### Issue Cards

- Hover effect (lifts up slightly)
- Color-coded labels
- User avatars
- Direct GitHub links

### Stats Section

- Gradient background
- Large, easy-to-read numbers
- Auto-updates

## 🔐 Security Considerations

### Public Access

By default, **anyone** can access your dashboard at your URL.

If you want to protect it:

### Add Basic Authentication

```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest

security = HTTPBasic()

@app.get("/")
async def root(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = compare_digest(credentials.username, "admin")
    correct_password = compare_digest(credentials.password, "your_password")

    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return templates.TemplateResponse("dashboard.html", {...})
```

### Add GitHub OAuth

Allow only authorized GitHub users to view the dashboard:

```bash
pip install authlib
```

Implement GitHub OAuth login flow.

## 🐛 Troubleshooting

### Issue: Dashboard shows no issues

**Causes**:

1. No issues have been created yet
2. Server was restarted (in-memory data lost)
3. Webhook isn't working

**Solution**:

1. Create a test issue in a repo where the app is installed
2. Check webhook deliveries in GitHub App settings
3. Check server logs for errors

### Issue: Dashboard doesn't load

**Causes**:

1. Templates or static directories missing
2. Port already in use

**Solution**:

```bash
# Check if directories exist
ls -la templates/ static/

# Create if missing
mkdir -p templates static
```

### Issue: Styles not loading

**Cause**: Static files not being served

**Solution**: Ensure this line is in `app.py`:

```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

## 🚀 Performance Tips

### For High Traffic

If you expect many issues:

1. **Use a database** instead of in-memory storage
2. **Add pagination** to load issues in chunks
3. **Add caching** with Redis
4. **Use WebSockets** for real-time updates

### WebSocket Example (Real-Time Updates)

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Send new issues in real-time
        await websocket.send_json({"issues": recent_issues})
        await asyncio.sleep(5)
```

## 📱 Mobile Responsive

The dashboard is fully responsive:

- ✅ Works on phones
- ✅ Works on tablets
- ✅ Works on desktop

The layout automatically adjusts based on screen size.

## 🎉 Next Steps

Enhance your dashboard with:

1. **Charts & Graphs**: Add issue trends over time
2. **Repository Breakdown**: Show issues per repository
3. **User Activity**: Track most active contributors
4. **Export Data**: Download issues as CSV/JSON
5. **Notifications**: Browser notifications for new issues
6. **Dark Mode**: Add theme toggle
7. **Analytics**: Track response times, comment success rate

## 📚 Related Files

- `app.py` - Backend logic
- `templates/dashboard.html` - HTML template
- `static/style.css` - Styling
- `requirements.txt` - Dependencies (includes Jinja2)

---

**Enjoy your beautiful dashboard! 🎨**
