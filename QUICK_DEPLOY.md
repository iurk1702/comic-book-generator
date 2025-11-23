# Quick Deployment Guide - Streamlit Cloud

## 🚀 Fastest Way to Deploy (5 minutes)

### Step 1: Push to GitHub

```bash
cd /Users/vaarunaykaushal/Documents/iurk1702/comicBookGenerator

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/comic-book-generator.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Go to:** https://share.streamlit.io/
2. **Sign in** with GitHub
3. **Click "New app"**
4. **Fill in:**
   - Repository: `YOUR_USERNAME/comic-book-generator`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Python version: `3.11`
5. **Click "Advanced settings"**
6. **Add secrets:**
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   REPLICATE_API_TOKEN=your-actual-token-here
   ```
7. **Click "Deploy"**

### Step 3: Done! 🎉

Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## 🔄 Updating Your App

Just push to GitHub:
```bash
git add .
git commit -m "Update"
git push
```

Streamlit Cloud will automatically redeploy!

---

## ⚠️ Important Notes

- **Never commit `.env` file** - it's already in `.gitignore`
- **Use Streamlit Cloud secrets** for API keys (not .env file)
- **Free tier limitations:**
  - Apps may sleep after inactivity
  - Limited CPU/memory (may be slow for large comics)
  - Output files don't persist (they're deleted when app restarts)

---

## 🐛 Troubleshooting

**App won't start:**
- Check that `streamlit_app.py` is in the root directory
- Verify Python version is 3.10 or 3.11
- Check logs in Streamlit Cloud dashboard

**API errors:**
- Verify secrets are set correctly (no quotes, no spaces)
- Check API keys are valid and have credits

**Import errors:**
- Check `requirements.txt` includes all dependencies
- Look at build logs in Streamlit Cloud

---

For more deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md)

