# IMDB Movie Browser - Deployment Guide

## Quick Start (Local Testing)

### 1. Prerequisites
```bash
# Python 3.11+ installed
python3 --version

# Database file exists
ls ../imdb_dataset.db
```

### 2. Install Dependencies
```bash
cd imdb_web_app
pip3 install -r requirements.txt
```

### 3. Run Development Server
```bash
python3 app.py
```

Visit: http://localhost:5000

**Note:** Development server is NOT for production use!

---

## Production Deployment Options

### Option 1: Render.com (RECOMMENDED) ⭐

#### Why Render?
- ✓ Free tier: 750 hours/month
- ✓ Auto-deploy from GitHub
- ✓ Free HTTPS
- ✓ Custom domains
- ✓ Easy setup

#### Step-by-Step:

**1. Prepare Files**
```bash
cd imdb_web_app
# Ensure these files exist:
ls app.py requirements.txt render.yaml
```

**2. Copy Database**
```bash
# Database MUST be in same directory as app.py
cp ../imdb_dataset.db ./imdb_dataset.db
```

**3. Create GitHub Repository**
```bash
git init
git add .
git commit -m "Initial commit: IMDB Movie Browser"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/imdb-movie-browser.git
git push -u origin main
```

**4. Deploy on Render**

Go to: https://render.com

- Click "New" → "Web Service"
- Connect your GitHub repository
- Render auto-detects `render.yaml`
- Click "Create Web Service"
- Wait 3-5 minutes for deployment

**5. Access Your Site**
URL: `https://your-app-name.onrender.com`

#### Render Configuration

File: `render.yaml`
```yaml
services:
  - type: web
    name: imdb-movie-browser
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn app:app"
    healthCheckPath: /
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### Important Notes:
- **Sleep Mode:** Free tier sleeps after 15 min inactivity
- **Wake Time:** ~30 seconds on first request
- **Database:** Include in repo or use persistent disk (paid)
- **Size Limit:** 500MB including database

---

### Option 2: Railway.app 🚂

#### Why Railway?
- ✓ $5 free credits/month
- ✓ No sleep mode
- ✓ GitHub integration
- ✓ Persistent storage

#### Step-by-Step:

**1. Prepare Files**
```bash
# Create Procfile for Railway
echo "web: gunicorn app:app" > Procfile

# Copy database
cp ../imdb_dataset.db ./imdb_dataset.db
```

**2. Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

**3. Deploy on Railway**

Go to: https://railway.app

- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your repository
- Railway auto-detects Python
- Click "Deploy"

**4. Add Environment Variables (Optional)**
- Dashboard → Variables
- Add: `PYTHON_VERSION=3.11`

**5. Access Your Site**
URL: `https://your-app.up.railway.app`

#### Railway Notes:
- **Credits:** $5/month = ~500 hours
- **Storage:** 1GB persistent disk
- **No Sleep:** Always on
- **Monitoring:** Built-in metrics

---

### Option 3: PythonAnywhere 🐍

#### Why PythonAnywhere?
- ✓ True 24/7 (no sleep)
- ✓ No credit card needed
- ✓ Easy Flask setup
- ✓ 512MB storage

#### Step-by-Step:

**1. Sign Up**
Go to: https://www.pythonanywhere.com
Create free account

**2. Upload Files**
- Dashboard → Files
- Upload all files from `imdb_web_app/`
- Upload `imdb_dataset.db`

**3. Create Web App**
- Dashboard → Web
- "Add a new web app"
- Choose "Flask"
- Python 3.10+
- Set path to `/home/USERNAME/imdb_web_app/app.py`

**4. Configure WSGI**
Edit `/var/www/USERNAME_pythonanywhere_com_wsgi.py`:
```python
import sys
path = '/home/USERNAME/imdb_web_app'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

**5. Reload Web App**
Click "Reload" button

**6. Access Your Site**
URL: `https://USERNAME.pythonanywhere.com`

#### PythonAnywhere Notes:
- **Storage:** 512MB total (DB + code)
- **URL:** Subdomain only (custom domain = paid)
- **Requests:** 100K/day limit
- **Speed:** Slower SQLite performance

---

## Database Management

### Option A: Include in Git (Simple)

```bash
# Add database to repo
git add imdb_dataset.db
git commit -m "Add database"
git push
```

**Pros:**
- Simple deployment
- No extra steps

**Cons:**
- Large repo size (~75MB)
- Updates require new commit
- GitHub has 100MB file limit

### Option B: Upload Separately (Better)

```bash
# Add to .gitignore
echo "imdb_dataset.db" >> .gitignore

# Upload via dashboard/FTP after deployment
```

**Pros:**
- Smaller repo
- Easy to update database
- Can use larger databases

**Cons:**
- Extra deployment step
- Manual upload needed

### Option C: Persistent Disk (Best for Production)

**Render:**
- Add persistent disk in dashboard
- Mount at `/mnt/data`
- Update `DATABASE_PATH` to `/mnt/data/imdb_dataset.db`

**Railway:**
- Volumes automatically persistent
- Database survives redeploys

---

## Environment Variables

Optional configuration via environment variables:

```bash
# Custom database path
export DATABASE_PATH="/path/to/imdb_dataset.db"

# Flask settings
export FLASK_ENV=production
export FLASK_DEBUG=0

# Server settings
export PORT=5000
export WORKERS=4
```

---

## Performance Tuning

### Gunicorn Workers

Default: 1 worker (included in `render.yaml`)

For more traffic:
```bash
# In render.yaml or Procfile
gunicorn app:app --workers 4 --threads 2
```

**Rule of thumb:** `(2 x CPU cores) + 1`

Free tiers usually have 1 CPU, so 3 workers max.

### Database Optimization

Already included in `app.py`:
```python
PRAGMA journal_mode=WAL
PRAGMA cache_size=-64000
PRAGMA temp_store=MEMORY
PRAGMA synchronous=NORMAL
PRAGMA mmap_size=268435456
```

### Caching (Advanced)

Add Redis caching for frequently searched queries:
```python
# Install: pip install redis flask-caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/search')
@cache.cached(timeout=300, query_string=True)
def api_search():
    # ...
```

---

## Updating the Deployment

### Update Code
```bash
# Make changes locally
git add .
git commit -m "Updated search functionality"
git push origin main

# Render/Railway auto-deploy
# PythonAnywhere: manual upload + reload
```

### Update Database
```bash
# Rebuild locally
python3 ../fix_country_data.py
python3 ../convert_to_sqlite.py

# Upload new database to hosting
# Or push to GitHub if using Option A
```

### Update Dependencies
```bash
# Edit requirements.txt
# Commit and push
# Platform will reinstall automatically
```

---

## Monitoring & Logs

### Render
- Dashboard → Logs tab
- Real-time log streaming
- Search/filter logs

### Railway
- Dashboard → Deployments → Logs
- Metrics tab for usage stats

### PythonAnywhere
- Dashboard → Web → Log files
- Error log and server log

### Check Health
```bash
curl https://your-app.onrender.com/
# Should return 200 OK
```

---

## Troubleshooting

### "Application Error" or 500 Error

**Check logs first!**

Common causes:
1. Database file missing
2. Wrong file paths
3. Missing dependencies
4. Python version mismatch

**Solutions:**
```bash
# Verify database exists
ls imdb_dataset.db

# Test locally first
python3 app.py

# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall
```

### "Module not found"

```bash
# requirements.txt incomplete
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Fix dependencies"
git push
```

### Database Locked

SQLite locks can happen with high concurrency:

**Solution:** Use WAL mode (already enabled in code)

Or switch to PostgreSQL for production:
```bash
# Install psycopg2
pip install psycopg2-binary

# Update app.py to use PostgreSQL
# (requires code changes)
```

### Slow Performance

1. **Reduce result limit:** Change default from 100 to 50
2. **Add pagination:** Load results in batches
3. **Optimize queries:** Check EXPLAIN QUERY PLAN
4. **Upgrade tier:** More RAM/CPU

### Out of Memory

Free tiers have limited RAM (512MB):

1. **Reduce cache size:**
```python
cur.execute("PRAGMA cache_size=-32000")  # 32MB instead of 64MB
```

2. **Reduce mmap size:**
```python
cur.execute("PRAGMA mmap_size=134217728")  # 128MB instead of 256MB
```

3. **Limit concurrent requests:** Use fewer Gunicorn workers

---

## Security Checklist

Before deploying:

- [ ] `FLASK_DEBUG=False` in production
- [ ] `app.run(debug=False)` or use Gunicorn
- [ ] No hardcoded secrets in code
- [ ] `.gitignore` includes sensitive files
- [ ] HTTPS enabled (automatic on Render/Railway)
- [ ] SQL injection protection (parameterized queries ✓)
- [ ] XSS protection (HTML escaping ✓)
- [ ] IMDB attribution visible on all pages ✓

---

## Cost Breakdown

### Free Tiers

| Platform | Hours/Month | Storage | Custom Domain | Sleep Mode |
|----------|-------------|---------|---------------|------------|
| Render | 750 | 500MB | ✓ Free | Yes (15 min) |
| Railway | ~500 ($5 credit) | 1GB | ✓ Free | No |
| PythonAnywhere | 24/7 | 512MB | ✗ Paid | No |

### Paid Upgrades

**Render:**
- Starter: $7/month (no sleep, custom domain)
- Standard: $25/month (more resources)

**Railway:**
- Pay-as-you-go: $0.000463/GB-hour
- Typical: $5-20/month for small app

**PythonAnywhere:**
- Hacker: $5/month (custom domain)
- Web Developer: $12/month (more resources)

---

## Recommended Setup

**For hobby/portfolio:**
- Use **Render** (free tier)
- Include database in Git (if <100MB)
- Accept sleep mode

**For active users:**
- Use **Railway** (always-on)
- $5/month budget
- Persistent storage

**For 24/7 reliability:**
- Upgrade to **Render Starter** ($7/month)
- Or **Railway** with budget
- Monitor usage

---

## Next Steps After Deployment

1. **Test thoroughly:**
   - Try all filters
   - Check mobile responsiveness
   - Test on different browsers

2. **Share URL:**
   - Add to portfolio
   - Share with friends
   - Post on social media (remember: non-commercial!)

3. **Monitor usage:**
   - Check logs regularly
   - Watch for errors
   - Monitor bandwidth

4. **Update regularly:**
   - Refresh IMDB data monthly
   - Update dependencies
   - Add new features

5. **Get feedback:**
   - Ask users what they want
   - Fix bugs quickly
   - Improve UX

---

## Support

- **IMDB Data Issues:** imdb-data-interest@imdb.com
- **Hosting Support:** Check platform docs
- **Application Issues:** Review ARCHITECTURE.md

Good luck with your deployment! 🚀
