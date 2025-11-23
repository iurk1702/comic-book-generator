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
        os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")
        # Using a comic book style model
        self.model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
    
    def generate_panel_image(self, scene_description: str, panel_number: int, style: str = "comic book"):
        """
        Generate an image for a comic panel.
        
        Args:
            scene_description: Detailed scene description
            panel_number: Panel number for consistency
            style: Art style (default: comic book)
        
        Returns:
            PIL Image object
        """
        prompt = f"{scene_description}, {style} style, vibrant colors, dynamic composition, comic book illustration"
        
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

