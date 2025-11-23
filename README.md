# Comic Book Generator v1

A simple AI-powered comic book generator that creates 3-5 panel comic strips with narration.

## Version Control

This project uses Git for version control. The repository is initialized and ready to use.

**Current branch:** `main`

**To check status:**
```bash
git status
```

**To see commit history:**
```bash
git log --oneline
```

## Features (v1)
- **Story Generation**: LLM generates a short story split into 3-5 panels
- **Image Generation**: Stable Diffusion creates comic-style images for each panel
- **Narration**: Text-to-speech adds voice narration
- **Predefined Characters**: Limited set of characters for consistency

## Setup

1. Virtual environment is already created. Activate it:
```bash
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file (copy from .env.example if needed)
# Add your API keys:
# - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys
# - REPLICATE_API_TOKEN: Get from https://replicate.com/account/api-tokens
```

## API Keys Required

- **OpenAI API Key**: For story generation (GPT-4o-mini) and text-to-speech
- **Replicate API Token**: For Stable Diffusion image generation

## Quick Start

1. **Set up API keys** (see [SETUP.md](SETUP.md) for detailed instructions):
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-key-here" > .env
   echo "REPLICATE_API_TOKEN=your-token-here" >> .env
   ```

2. **Activate virtual environment and run**:
   ```bash
   source venv/bin/activate
   python main.py
   ```

3. **Follow the prompts** to generate your comic!

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Project Status

✅ **Working Features:**
- Story generation with LLM
- Image generation with Stable Diffusion
- Text-to-speech narration
- Comic panel assembly
- Error handling and validation

⚠️ **Requirements:**
- OpenAI API key (for story + narration)
- Replicate API token (for images)
- Python 3.8+ with virtual environment

## Usage

```bash
python main.py
```

## Architecture

- `story_generator.py`: LLM module for story generation
- `image_generator.py`: Stable Diffusion integration for panel images
- `narration_generator.py`: TTS for narration
- `comic_assembler.py`: Combines panels into final comic
- `main.py`: Main workflow orchestrator

