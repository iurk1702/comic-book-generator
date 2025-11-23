"""
Image generation module using Stable Diffusion via Replicate API.
Generates comic book style images for each panel.
"""
import os
import replicate
from dotenv import load_dotenv
from PIL import Image
import io
import requests
import time
from replicate.exceptions import ReplicateError

load_dotenv()

class ImageGenerator:
    def __init__(self):
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables. Please set it in .env file.")
        os.environ["REPLICATE_API_TOKEN"] = api_token
        # Using Stable Diffusion XL model for better quality
        self.model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        self.character_descriptions = {}  # Store character descriptions for consistency
        # Rate limiting: 6 requests per minute = 10 seconds between requests
        self.min_delay_between_requests = 10  # seconds
        self.last_request_time = 0
    
    def set_character_descriptions(self, character_descriptions: dict):
        """Set character descriptions to use for consistent character appearance."""
        self.character_descriptions = character_descriptions
    
    def generate_panel_image(self, scene_description: str, panel_number: int, style: str = "comic book", characters_in_scene: list = None):
        """
        Generate an image for a comic panel with character consistency.
        
        Args:
            scene_description: Detailed scene description
            panel_number: Panel number for consistency
            style: Art style (default: comic book)
            characters_in_scene: List of character names appearing in this scene
        
        Returns:
            PIL Image object
        """
        # Build character consistency prompt
        character_prompt = ""
        if characters_in_scene and self.character_descriptions:
            char_details = []
            for char in characters_in_scene:
                if char in self.character_descriptions:
                    char_desc = self.character_descriptions[char]['description']
                    detailed = char_desc.get('detailed_description', char_desc.get('description', ''))
                    if detailed:
                        char_details.append(f"{char}: {detailed}")
            
            if char_details:
                character_prompt = ", ".join(char_details) + ", "
        
        # Combine scene description with character consistency
        prompt = f"{character_prompt}{scene_description}, {style} style, vibrant colors, dynamic composition, comic book illustration, consistent character appearance"
        
        # Rate limiting: ensure minimum delay between requests
        self._wait_for_rate_limit()
        
        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 5  # Start with 5 seconds
        
        for attempt in range(max_retries):
            try:
                output = replicate.run(
                    self.model,
                    input={
                        "prompt": prompt,
                        "negative_prompt": "blurry, low quality, distorted, text, watermark",
                        "num_outputs": 1,
                        "guidance_scale": 7.5,
                        "num_inference_steps": 30
                    }
                )
                
                # Download the image
                if output and len(output) > 0:
                    image_url = output[0] if isinstance(output, list) else output
                    response = requests.get(image_url)
                    image = Image.open(io.BytesIO(response.content))
                    self.last_request_time = time.time()
                    return image
                else:
                    raise Exception("No image generated")
                    
            except ReplicateError as e:
                # Handle rate limiting (429) and other API errors
                if hasattr(e, 'status') and e.status == 429:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"Rate limit exceeded after {max_retries} attempts. Using placeholder.")
                        return self._create_placeholder(panel_number, "Rate limit exceeded")
                else:
                    print(f"Replicate API error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return self._create_placeholder(panel_number, f"API error: {str(e)[:50]}")
                    
            except Exception as e:
                print(f"Error generating image (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return self._create_placeholder(panel_number, f"Generation failed: {str(e)[:50]}")
        
        # If all retries failed
        return self._create_placeholder(panel_number, "All retries failed")
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay_between_requests:
            wait_time = self.min_delay_between_requests - time_since_last
            print(f"Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
    
    def _create_placeholder(self, panel_number: int, error_message: str = "Image generation failed"):
        """Create a placeholder image if generation fails"""
        img = Image.new('RGB', (512, 512), color=(200, 200, 200))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()
        
        # Wrap text for better display
        text = f"Panel {panel_number}\n{error_message}"
        lines = text.split('\n')
        y_offset = 200
        for line in lines:
            draw.text((150, y_offset), line, fill=(0, 0, 0), font=font, align="center")
            y_offset += 30
        
        return img

