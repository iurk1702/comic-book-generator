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
                return image
            else:
                raise Exception("No image generated")
                
        except Exception as e:
            print(f"Error generating image: {e}")
            # Return a placeholder image
            return self._create_placeholder(panel_number)
    
    def _create_placeholder(self, panel_number: int):
        """Create a placeholder image if generation fails"""
        img = Image.new('RGB', (512, 512), color=(200, 200, 200))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
        draw.text((150, 240), f"Panel {panel_number}\n(Image generation failed)", 
                 fill=(0, 0, 0), font=font, align="center")
        return img

