# Web UI Guide

## Launching the UI

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Launch Streamlit:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Browser opens automatically** at `http://localhost:8501`

   If it doesn't open automatically, navigate to that URL in your browser.

## Using the UI

### Main Interface

1. **Story Input:**
   - Enter your story idea in the text area
   - Be descriptive for better results
   - Example: "A hero saves the city from a giant robot"

2. **Panel Selection:**
   - Use the slider to choose 3-5 panels
   - More panels = longer story but more generation time

3. **Generate Button:**
   - Click "🚀 Generate Comic" to start
   - Progress will be shown in real-time

### Sidebar Configuration

- **Character Selection:**
  - Choose which characters to include (hero, villain, sidekick)
  - Default: hero and villain

- **Narration Voice:**
  - Select from 6 voice options:
    - `alloy` - Neutral, balanced
    - `echo` - Clear, professional
    - `fable` - Warm, friendly
    - `onyx` - Deep, authoritative
    - `nova` - Bright, energetic
    - `shimmer` - Soft, gentle

### During Generation

You'll see:
- **Progress bar** showing overall completion
- **Status messages** for each step:
  - Story generation
  - Image generation (with previews)
  - Narration generation
  - Comic assembly

### After Generation

1. **Story Preview:**
   - Expandable section showing the generated story
   - View scene descriptions and narration text

2. **Individual Panels:**
   - Each panel displayed in a column
   - Images appear as they're generated

3. **Final Comic:**
   - Complete assembled comic strip
   - All panels combined vertically

4. **Download Section:**
   - Download the final comic as PNG
   - Download individual narration MP3 files

5. **Audio Playback:**
   - Listen to narration directly in the browser
   - One audio player per panel

## Tips

- **Better Stories:** Be specific in your story idea
- **Faster Generation:** Use fewer panels (3 instead of 5)
- **Better Images:** More detailed scene descriptions = better images
- **Voice Selection:** Try different voices for different character types

## Troubleshooting

### UI won't start
- Make sure virtual environment is activated
- Check that Streamlit is installed: `pip install streamlit`

### API Key Errors
- Check that `.env` file exists and has correct keys
- Restart Streamlit after adding keys

### Generation Fails
- Check your API key quotas/credits
- Look at error messages in the UI
- Try with a simpler story prompt

### Images Don't Show
- Check internet connection (images are downloaded from Replicate)
- Wait for generation to complete
- Refresh the page if needed

## Keyboard Shortcuts

- `R` - Rerun the app
- `C` - Clear cache
- `?` - Show keyboard shortcuts

## Stopping the Server

Press `Ctrl+C` in the terminal where Streamlit is running.

