# Configuration Summary - What You Need

## ✅ Required: 2 API Keys

You need to provide **exactly 2 API keys** in a `.env` file:

### 1. OpenAI API Key
```env
OPENAI_API_KEY=sk-your-key-here
```
- **Where to get it:** https://platform.openai.com/api-keys
- **What it's used for:**
  - Story generation (GPT-4o-mini)
  - Text-to-speech narration
- **Cost:** ~$0.01-0.05 per comic

### 2. Replicate API Token
```env
REPLICATE_API_TOKEN=your-token-here
```
- **Where to get it:** https://replicate.com/account/api-tokens
- **What it's used for:**
  - Image generation (Stable Diffusion XL)
- **Cost:** ~$0.012-0.016 per comic (4 panels)

---

## 📝 How to Set Up

1. **Create `.env` file:**
   ```bash
   cd /Users/vaarunaykaushal/Documents/iurk1702/comicBookGenerator
   touch .env
   ```

2. **Add your keys:**
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **That's it!** The app will automatically load these keys.

---

## 🔧 Currently Hardcoded (No Action Needed)

These are set in code and work out of the box:

- **OpenAI Model:** `gpt-4o-mini` (cheap, fast)
- **Temperature:** `0.8` (balanced creativity)
- **Image Model:** Stable Diffusion XL
- **Panel Size:** 800x600 pixels
- **Default Voice:** `alloy` (can be changed in UI)

You don't need to configure these - they're already optimized for v1.

---

## 📚 Detailed Guides

- **Full API Keys Guide:** See [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)
- **Setup Instructions:** See [SETUP.md](SETUP.md)
- **UI Usage:** See [UI_GUIDE.md](UI_GUIDE.md)

---

## ⚡ Quick Start

```bash
# 1. Create .env file
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "REPLICATE_API_TOKEN=your-token" >> .env

# 2. Run the UI
source venv/bin/activate
streamlit run streamlit_app.py
```

That's all you need! 🎉

