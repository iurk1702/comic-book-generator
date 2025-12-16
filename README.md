# Comic Book Generator v1

An AI-powered comic book generator that transforms your story ideas into fully illustrated comic books with narration, available in multiple formats (PNG, PDF, and video).

## 🌐 Live Demo

**Try it now:** [https://comic-book-generator-mgjkugmgofh2xjnzydkjbq.streamlit.app/](https://comic-book-generator-mgjkugmgofh2xjnzydkjbq.streamlit.app/)

## About This Project

The Comic Book Generator is an end-to-end AI application that automates the entire comic book creation process. Simply provide a story idea, and the system will:

1. **Generate a Complete Story**: Uses GPT-4o-mini to create a structured narrative broken down into multiple panels with scene descriptions and narration text.

2. **Create Consistent Characters**: Supports both existing comic book characters (from a predefined database) and custom characters. Generates reference images to maintain visual consistency across all panels.

3. **Generate Comic-Style Images**: Uses Stable Diffusion via Replicate to create high-quality, comic-style illustrations for each panel, ensuring characters look consistent throughout the story.

4. **Add Voice Narration**: Converts the narration text into natural-sounding speech using OpenAI's text-to-speech API, with multiple voice options available.

5. **Assemble Multiple Formats**: Combines everything into:
   - **PNG**: High-resolution image of the complete comic
   - **PDF**: Print-ready comic book format
   - **MP4 Video**: Animated comic with synchronized narration

The application features both a user-friendly web interface (built with Streamlit) and a command-line interface, making it accessible for both casual users and developers.

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
- **Story Generation**: LLM generates a complete story split into multiple panels (configurable pages and panels per page)
- **Image Generation**: Stable Diffusion creates comic-style images for each panel with character consistency
- **Character Management**: Support for both existing comic book characters and custom character creation
- **Character Consistency**: Generates reference images to maintain visual consistency across all panels
- **Narration**: Text-to-speech adds voice narration with multiple voice options
- **Multiple Export Formats**: Generate comics as PNG, PDF, and MP4 video with synchronized narration
- **Web UI**: User-friendly Streamlit interface for easy comic creation
- **CLI Support**: Command-line interface for programmatic usage

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

### Option 1: Web UI (Recommended)

1. **Set up API keys** (see [SETUP.md](SETUP.md) for detailed instructions):
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-key-here" > .env
   echo "REPLICATE_API_TOKEN=your-token-here" >> .env
   ```

2. **Activate virtual environment and launch UI**:
   ```bash
   source venv/bin/activate
   streamlit run streamlit_app.py
   ```

3. **Open your browser** - Streamlit will automatically open at `http://localhost:8501`

4. **Fill in the form** and click "Generate Comic"!

### Option 2: Command Line

1. **Set up API keys** (same as above)

2. **Run the CLI version**:
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
- `main.py`: CLI workflow orchestrator
- `streamlit_app.py`: Web UI for the application

