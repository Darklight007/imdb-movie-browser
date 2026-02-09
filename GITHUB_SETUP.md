# GitHub Setup Guide

Complete step-by-step instructions for setting up your IMDB Movie Browser on GitHub and deploying it.

## Prerequisites

- GitHub account (free): https://github.com/signup
- Git installed on your computer
- IMDB web app files ready

## Step 1: Install Git (if needed)

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install git
```

### macOS
```bash
# Using Homebrew
brew install git

# Or download from: https://git-scm.com/download/mac
```

### Windows
Download from: https://git-scm.com/download/win

### Verify Installation
```bash
git --version
# Should show: git version 2.x.x
```

## Step 2: Configure Git

Set your name and email (used in commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Verify:
```bash
git config --list
```

## Step 3: Create GitHub Repository

### Via GitHub Website:

1. Go to: https://github.com
2. Click "+" in top-right → "New repository"
3. Fill in details:
   - **Repository name:** `imdb-movie-browser`
   - **Description:** `A free web app for searching movies from IMDB datasets`
   - **Public** (required for free hosting)
   - ✓ Check "Add README file" → **UNCHECK** (we have our own)
   - ✓ **Add .gitignore** → Select "Python"
   - License → Skip (we'll add manually)
4. Click "Create repository"

### Via GitHub CLI (Alternative):

```bash
# Install GitHub CLI first
# Ubuntu: sudo apt install gh
# macOS: brew install gh

gh auth login
gh repo create imdb-movie-browser --public --description "IMDB Movie Browser Web App"
```

## Step 4: Prepare Your Local Repository

Navigate to your web app directory:

```bash
cd /home/h/Documents/Python/imdb_web_app
```

### Initialize Git

```bash
git init
```

This creates a `.git` folder (hidden).

### Check What's Included

```bash
git status
```

You should see:
- app.py
- templates/
- static/
- requirements.txt
- render.yaml
- README.md
- etc.

## Step 5: Decide on Database Strategy

**Important:** You have two options for the database file:

### Option A: Include Database in Git (Simple)

**Pros:** Easy deployment, one-step process
**Cons:** Large repo, 100MB GitHub limit

```bash
# Check database size
ls -lh imdb_dataset.db

# If under 100MB, you can include it:
# (Don't add to .gitignore)
```

**⚠️ Warning:** Your database is ~75MB, so this works, but:
- Repo will be large
- Cloning will be slow
- Updates require new commits

### Option B: Exclude Database (Recommended)

**Pros:** Smaller repo, easier to update
**Cons:** Requires manual upload after deployment

```bash
# Add to .gitignore
echo "imdb_dataset.db" >> .gitignore
echo "*.db" >> .gitignore
echo "*.sqlite" >> .gitignore
```

**Note:** You'll upload the database separately after deploying (see DEPLOYMENT.md).

## Step 6: Add Files to Git

### Add All Files

```bash
git add .
```

This stages all files except those in `.gitignore`.

### Verify What's Staged

```bash
git status
```

Should show all files in green (staged).

### Create First Commit

```bash
git commit -m "Initial commit: IMDB Movie Browser web application

- Flask backend with SQLite
- Responsive HTML/CSS frontend
- Advanced search and filtering
- Ready for Render/Railway deployment
- IMDB non-commercial dataset attribution"
```

## Step 7: Connect to GitHub

Get your repository URL from GitHub:
- Go to your repo page
- Click green "Code" button
- Copy HTTPS URL (e.g., `https://github.com/YOUR_USERNAME/imdb-movie-browser.git`)

### Add Remote

```bash
git remote add origin https://github.com/YOUR_USERNAME/imdb-movie-browser.git
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Verify Remote

```bash
git remote -v
```

Should show:
```
origin  https://github.com/YOUR_USERNAME/imdb-movie-browser.git (fetch)
origin  https://github.com/YOUR_USERNAME/imdb-movie-browser.git (push)
```

## Step 8: Push to GitHub

### Set Default Branch Name

```bash
# Rename current branch to 'main' (GitHub default)
git branch -M main
```

### Push Code

```bash
git push -u origin main
```

**First time:** You'll be prompted for GitHub credentials:
- Username: your GitHub username
- Password: **Use a Personal Access Token** (not your password!)

#### Creating a Personal Access Token:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Git Access"
4. Expiration: 90 days (or longer)
5. Scopes: ✓ Check `repo` (all sub-options)
6. Click "Generate token"
7. **Copy the token** (you can't see it again!)
8. Use this token as your password when pushing

### Verify on GitHub

Go to your repository URL in browser. You should see all your files!

## Step 9: Add License (Optional but Recommended)

### Create LICENSE File

```bash
cat > LICENSE << 'EOF'
MIT License with IMDB Data Attribution

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

IMDB DATA ATTRIBUTION:
This software uses data from IMDB's Non-Commercial Datasets.
Information courtesy of IMDb (https://www.imdb.com). Used with permission.
Data is for non-commercial use only. For commercial licensing, contact licensing@imdb.com

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### Commit License

```bash
git add LICENSE
git commit -m "Add MIT license with IMDB attribution"
git push
```

## Step 10: Update README with Your Info

Edit README.md:

```bash
# Replace placeholder with your actual GitHub username
sed -i 's/YOUR_USERNAME/your-actual-username/g' README.md

# Add real screenshots (optional)
# Replace placeholder URLs with actual screenshots

git add README.md
git commit -m "Update README with actual GitHub username"
git push
```

## Step 11: Deploy to Render

Now that your code is on GitHub, deploy it!

### Quick Deploy:

1. Go to: https://render.com
2. Sign up (use GitHub login)
3. Click "New" → "Web Service"
4. Connect GitHub → Authorize Render
5. Select `imdb-movie-browser` repository
6. Render auto-detects `render.yaml`
7. Click "Create Web Service"
8. Wait 3-5 minutes

### Upload Database (if excluded from Git):

After deployment:
1. Render Dashboard → Your service → "Shell"
2. Click "Upload File" → Select `imdb_dataset.db`
3. Or use Render Disk (persistent storage)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Common Git Commands (Reference)

### Daily Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push

# Pull latest changes (if working from multiple computers)
git pull
```

### Viewing History

```bash
# View commit history
git log

# View recent commits (compact)
git log --oneline -10

# View changes in last commit
git show
```

### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- filename

# Unstage file
git reset HEAD filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - DANGEROUS!
git reset --hard HEAD~1
```

### Branching (Advanced)

```bash
# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch into main
git checkout main
git merge feature-name

# Delete branch
git branch -d feature-name
```

## Troubleshooting

### Authentication Failed

**Problem:** Can't push to GitHub

**Solution:** Use Personal Access Token instead of password:
1. Generate token: https://github.com/settings/tokens
2. Use token as password when prompted

### Large File Error

**Problem:** "file exceeds GitHub's file size limit of 100.00 MB"

**Solution:**
```bash
# Remove database from Git
git rm --cached imdb_dataset.db
echo "imdb_dataset.db" >> .gitignore
git commit -m "Remove database from Git"
git push
```

Upload database separately to hosting platform.

### Wrong Remote URL

**Problem:** Pushing to wrong repository

**Solution:**
```bash
# Check current remote
git remote -v

# Change remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/imdb-movie-browser.git

# Verify
git remote -v
```

### Merge Conflicts

**Problem:** Conflicts when pulling

**Solution:**
```bash
# See conflicting files
git status

# Edit files to resolve conflicts
# Look for <<<<<<< HEAD markers

# After resolving:
git add .
git commit -m "Resolve merge conflicts"
git push
```

### Forgot to Commit

**Problem:** Pushed without committing changes

**Solution:**
```bash
# Stage changes
git add .

# Commit
git commit -m "Description"

# Push
git push
```

## Best Practices

### Commit Messages

**Good:**
```bash
git commit -m "Add country filter to search form"
git commit -m "Fix: Database connection timeout on large queries"
git commit -m "Update: Improve mobile responsive design"
```

**Bad:**
```bash
git commit -m "fix"
git commit -m "updates"
git commit -m "asdf"
```

### Commit Frequency

- Commit after each feature/fix
- Don't commit broken code
- Commit before making risky changes
- Push at end of work session

### .gitignore Best Practices

Always ignore:
```
__pycache__/
*.pyc
.env
*.log
.DS_Store
.vscode/
*.swp
```

Maybe ignore:
```
imdb_dataset.db  # Large files
*.db             # All databases
```

## Next Steps

1. ✅ Code on GitHub
2. ✅ Deployed to Render/Railway
3. 🎯 Share your URL!
4. 📊 Monitor usage
5. 🚀 Add new features
6. 🔄 Update regularly

## Resources

- **Git Documentation:** https://git-scm.com/doc
- **GitHub Guides:** https://guides.github.com
- **Git Cheat Sheet:** https://education.github.com/git-cheat-sheet-education.pdf
- **Interactive Git Tutorial:** https://learngitbranching.js.org

## Quick Reference Card

```bash
# Setup (once)
git init
git config --global user.name "Your Name"
git config --global user.email "email@example.com"
git remote add origin URL

# Daily workflow
git status                    # Check changes
git add .                     # Stage all changes
git commit -m "message"       # Commit changes
git push                      # Upload to GitHub
git pull                      # Download from GitHub

# Undo
git checkout -- file          # Discard changes
git reset HEAD file           # Unstage
git reset --soft HEAD~1       # Undo last commit

# Info
git log                       # View history
git diff                      # View changes
git branch                    # List branches
git remote -v                 # List remotes
```

---

**You're all set! Your IMDB Movie Browser is now on GitHub and ready to share with the world! 🎉**
