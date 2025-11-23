# Setup Guide - Getting Your Comic Book Generator Working

## Step 1: Install Dependencies

Dependencies are already installed in the virtual environment. If you need to reinstall:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Get API Keys

You need two API keys. **See [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) for detailed instructions.**

### Quick Summary:

**OpenAI API Key:**
- Get from: https://platform.openai.com/api-keys
- Used for: Story generation + Text-to-speech
- Cost: ~$0.01-0.05 per comic

**Replicate API Token:**
- Get from: https://replicate.com/account/api-tokens
- Used for: Image generation
- Cost: ~$0.012-0.016 per comic (4 panels)

## Step 3: Create .env File

**Easiest way - copy the example:**
```bash
cd /Users/vaarunaykaushal/Documents/iurk1702/comicBookGenerator
cp .env.example .env
```

Then edit `.env` and add your actual keys:

```env
OPENAI_API_KEY=sk-your-actual-key-here
REPLICATE_API_TOKEN=your-actual-token-here
```

**Important:** 
- Never commit the `.env` file to git! It's already in `.gitignore`.
- See [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) for detailed key setup instructions.

## Step 4: Test the Setup

Test that everything is configured correctly:

```bash
source venv/bin/activate
python main.py
```

If you see an error about missing API keys, check your `.env` file.

## Step 5: Generate Your First Comic!

Run the script and follow the prompts:

```bash
python main.py
```

Enter a story idea when prompted, and wait for the magic to happen!

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you created a `.env` file
- Check that the key name is exactly `OPENAI_API_KEY` (no typos)
- Make sure the `.env` file is in the `comicBookGenerator` directory

### "REPLICATE_API_TOKEN not found"
- Same as above, but for `REPLICATE_API_TOKEN`

### Import errors
- Make sure the virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### API errors during generation
- Check that your API keys are valid and have credits/quota
- For OpenAI: Check https://platform.openai.com/usage
- For Replicate: Check https://replicate.com/account

## Expected Output

When working correctly, you should see:
1. Story generation progress
2. Image generation for each panel
3. Narration generation
4. Final comic saved to `output/comic.png`
5. Narration files in `output/narration/`

Enjoy creating comics! 🎨

