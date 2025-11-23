# Comic Book Generator v1

A simple AI-powered comic book generator that creates 3-5 panel comic strips with narration.

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

Once you have your API keys set up in `.env`:

```bash
python main.py
```

Follow the prompts to generate your comic!

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

