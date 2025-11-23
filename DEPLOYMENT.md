# Deployment Guide

This guide covers deploying your Comic Book Generator to various platforms.

## 🚀 Recommended: Streamlit Cloud (Easiest)

Streamlit Cloud is the simplest way to deploy Streamlit apps for free.

### Prerequisites
1. GitHub account
2. Streamlit Cloud account (free at https://streamlit.io/cloud)

### Steps

1. **Push your code to GitHub:**
   ```bash
   cd /Users/vaarunaykaushal/Documents/iurk1702/comicBookGenerator
   git init  # if not already initialized
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/comic-book-generator.git
   git push -u origin main
   ```

2. **Sign up for Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub

3. **Deploy your app:**
   - Click "New app"
   - Select your repository
   - Set **Main file path**: `streamlit_app.py`
   - Set **Python version**: `3.11` (or 3.10)

4. **Add environment variables:**
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add:
     ```
     OPENAI_API_KEY=sk-your-key-here
     REPLICATE_API_TOKEN=your-token-here
     ```

5. **Deploy!**
   - Click "Deploy"
   - Your app will be live at `https://YOUR_APP_NAME.streamlit.app`

### Notes for Streamlit Cloud:
- ✅ Free tier available
- ✅ Automatic deployments on git push
- ✅ Built-in secrets management
- ⚠️ Free tier has resource limits (may be slow for large comics)
- ⚠️ Files are ephemeral (output files won't persist)

---

## 🐳 Alternative: Docker + Cloud Service

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Deploy to Railway (Recommended for Docker)

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   railway init
   ```

4. **Add environment variables:**
   ```bash
   railway variables set OPENAI_API_KEY=sk-your-key-here
   railway variables set REPLICATE_API_TOKEN=your-token-here
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

### Deploy to Render

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: comic-generator
       env: docker
       dockerfilePath: ./Dockerfile
       envVars:
         - key: OPENAI_API_KEY
           sync: false
         - key: REPLICATE_API_TOKEN
           sync: false
   ```

2. **Connect GitHub repo to Render**
3. **Set environment variables in Render dashboard**
4. **Deploy**

---

## ☁️ Alternative: Heroku

### Create files:

**`Procfile`:**
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**`runtime.txt`:**
```
python-3.11.0
```

**`setup.sh`:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
" > ~/.streamlit/config.toml
```

### Deploy:

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=sk-your-key-here
heroku config:set REPLICATE_API_TOKEN=your-token-here
git push heroku main
```

---

## 🔧 Pre-Deployment Checklist

- [ ] Update `.gitignore` to exclude sensitive files
- [ ] Remove any hardcoded API keys
- [ ] Test locally with environment variables
- [ ] Update `requirements.txt` with exact versions if needed
- [ ] Create deployment-specific config files
- [ ] Document environment variables needed

---

## 📝 Environment Variables

Your app needs these environment variables:

```bash
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...
```

**Never commit these to git!** Use platform-specific secrets management.

---

## 🐛 Troubleshooting

### "Module not found" errors
- Check `requirements.txt` includes all dependencies
- Ensure Python version matches (3.10 or 3.11 recommended)

### "API key not found" errors
- Verify environment variables are set correctly
- Check variable names match exactly (case-sensitive)

### Slow performance
- Free tiers have limited resources
- Consider upgrading or using a paid tier
- Optimize image sizes if needed

### File storage issues
- Output files may not persist on free tiers
- Consider using cloud storage (S3, etc.) for generated comics

---

## 💰 Cost Considerations

**Free Tier Limits:**
- Streamlit Cloud: Limited CPU/memory, may timeout on long operations
- Railway: $5/month free credit
- Render: Free tier with limitations

**API Costs (per comic):**
- OpenAI: ~$0.01-0.05
- Replicate: ~$0.012-0.016
- **Total: ~$0.02-0.07 per comic**

---

## 🎯 Recommended Approach

**For quick deployment:** Use Streamlit Cloud
**For production:** Use Railway or Render with Docker
**For enterprise:** Use AWS/GCP with proper infrastructure

