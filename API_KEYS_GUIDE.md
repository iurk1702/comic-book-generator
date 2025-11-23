# API Keys & Configuration Guide

## Required API Keys

You need **2 API keys** to run this application:

### 1. OpenAI API Key

**What it's used for:**
- Story generation (GPT-4o-mini model)
- Text-to-speech narration (TTS-1 model)

**How to get it:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Give it a name (e.g., "Comic Generator")
6. **Copy the key immediately** - you won't see it again!

**Cost:**
- GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- TTS-1: $15 per 1M characters
- Typical comic generation: ~$0.01-0.05 per comic

**Add to .env:**
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 2. Replicate API Token

**What it's used for:**
- Image generation (Stable Diffusion XL model)

**How to get it:**
1. Go to https://replicate.com/
2. Sign up or log in
3. Navigate to https://replicate.com/account/api-tokens
4. Click "Create token"
5. Give it a name (e.g., "Comic Generator")
6. Copy the token

**Cost:**
- Stable Diffusion XL: ~$0.003-0.004 per image
- Typical comic (4 panels): ~$0.012-0.016 per comic

**Add to .env:**
```env
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Setting Up Your .env File

1. **Copy the example file:**
   ```bash
   cd /Users/vaarunaykaushal/Documents/iurk1702/comicBookGenerator
   cp .env.example .env
   ```

2. **Edit the .env file:**
   ```bash
   # Use any text editor
   nano .env
   # or
   code .env
   ```

3. **Add your keys:**
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   REPLICATE_API_TOKEN=your-actual-token-here
   ```

4. **Save and verify:**
   - Make sure there are no quotes around the values
   - No spaces around the `=` sign
   - No trailing spaces

---

## Verifying Your Setup

### Test API Keys

**Test OpenAI:**
```bash
source venv/bin/activate
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('OpenAI key works!' if client else 'Error')"
```

**Test Replicate:**
```bash
source venv/bin/activate
python -c "import replicate; import os; from dotenv import load_dotenv; load_dotenv(); os.environ['REPLICATE_API_TOKEN'] = os.getenv('REPLICATE_API_TOKEN'); print('Replicate token works!' if os.getenv('REPLICATE_API_TOKEN') else 'Error')"
```

### Run the Application

If keys are set correctly, the app will start without errors:
```bash
streamlit run streamlit_app.py
```

---

## Cost Estimation

### Per Comic Generation (4 panels):

| Service | Usage | Cost |
|---------|-------|------|
| OpenAI (Story) | ~500 tokens | ~$0.0005 |
| OpenAI (TTS) | ~200 characters | ~$0.000003 |
| Replicate (Images) | 4 images | ~$0.012-0.016 |
| **Total** | | **~$0.013-0.017** |

**Monthly estimates:**
- 100 comics: ~$1.30-1.70
- 500 comics: ~$6.50-8.50
- 1000 comics: ~$13-17

---

## Security Best Practices

1. **Never commit .env file:**
   - It's already in `.gitignore`
   - Never share your API keys publicly

2. **Use environment-specific keys:**
   - Consider creating separate keys for development/production

3. **Monitor usage:**
   - Check OpenAI usage: https://platform.openai.com/usage
   - Check Replicate usage: https://replicate.com/account

4. **Set spending limits:**
   - OpenAI: Set usage limits in account settings
   - Replicate: Monitor usage dashboard

---

## Troubleshooting

### "OPENAI_API_KEY not found"
- Check that `.env` file exists in the project root
- Verify the key name is exactly `OPENAI_API_KEY` (case-sensitive)
- Make sure you activated the virtual environment
- Restart the app after adding keys

### "REPLICATE_API_TOKEN not found"
- Same checks as above
- Verify token name is exactly `REPLICATE_API_TOKEN`

### "Invalid API key" errors
- Verify keys are correct (no extra spaces)
- Check if keys have expired or been revoked
- Ensure you have credits/quota available

### Rate limit errors
- OpenAI: Check your tier limits
- Replicate: Free tier has rate limits
- Wait a few minutes and try again

---

## Optional: Making More Parameters Configurable

Currently, these are hardcoded but could be added to `.env`:

- `OPENAI_MODEL` - Which GPT model to use
- `OPENAI_TEMPERATURE` - Creativity level (0.0-2.0)
- `REPLICATE_MODEL` - Which image model to use
- `IMAGE_GUIDANCE_SCALE` - Image generation quality
- `PANEL_WIDTH/HEIGHT` - Comic panel dimensions
- `DEFAULT_TTS_VOICE` - Default narration voice

These are documented in `.env.example` for future use.

