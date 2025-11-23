"""
Character generator module for creating consistent character appearances.
Generates detailed character descriptions and reference images.
"""
import os
import json
import replicate
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import io
import requests
import time
from replicate.exceptions import ReplicateError

load_dotenv()

# Predefined character base descriptions
PREDEFINED_CHARACTERS = {
    "hero": {
        "base_description": "A brave superhero with a cape",
        "default_traits": "wears a colorful costume, has a heroic stance, confident expression"
    },
    "villain": {
        "base_description": "A menacing villain with dark powers",
        "default_traits": "wears dark clothing, has an intimidating presence, sinister expression"
    },
    "sidekick": {
        "base_description": "A loyal companion with special abilities",
        "default_traits": "younger appearance, supportive stance, determined expression"
    }
}

class CharacterGenerator:
    def __init__(self):
        # OpenAI for character descriptions
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=api_key)
        
        # Replicate for character images
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables.")
        os.environ["REPLICATE_API_TOKEN"] = api_token
        self.model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        # Rate limiting: 6 requests per minute = 10 seconds between requests
        self.min_delay_between_requests = 10  # seconds
        self.last_request_time = 0
    
    def generate_character_description(self, character_name: str, story_context: str = ""):
        """
        Generate a detailed, consistent character description using LLM.
        
        Args:
            character_name: Name of character (hero, villain, sidekick)
            story_context: Optional story context for character customization
        
        Returns:
            Dictionary with detailed character description
        """
        base_info = PREDEFINED_CHARACTERS.get(character_name, {
            "base_description": "A character",
            "default_traits": "distinctive appearance"
        })
        
        system_prompt = """You are a character designer for comic books. Create a detailed, specific description of a character's appearance that will be used consistently across multiple comic panels.

The description should include:
- Physical features (hair color, eye color, build, height)
- Clothing/costume details (colors, style, distinctive elements)
- Facial features (distinctive marks, expression style)
- Pose/body language characteristics
- Any unique visual identifiers

Make it specific enough that the same character will look consistent across different scenes. Return ONLY a JSON object with the description."""

        user_prompt = f"""Create a detailed visual description for a {character_name} character.
Base description: {base_info['base_description']}
Default traits: {base_info['default_traits']}
Story context: {story_context if story_context else 'General superhero story'}

Generate a detailed, specific description that ensures visual consistency."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7  # Lower temperature for more consistent descriptions
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON from response
            try:
                # Try direct JSON parse
                char_data = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    char_data = json.loads(json_match.group(1))
                else:
                    # Fallback: create structure from text
                    char_data = {"description": content, "detailed_description": content}
            
            # Ensure we have the required fields
            description = char_data.get("description", char_data.get("visual_description", base_info['base_description']))
            
            return {
                "name": character_name,
                "description": description,
                "detailed_description": char_data.get("detailed_description", description),
                "physical_features": char_data.get("physical_features", ""),
                "costume": char_data.get("costume", ""),
                "distinctive_features": char_data.get("distinctive_features", "")
            }
            
        except Exception as e:
            print(f"Error generating character description: {e}")
            # Fallback to base description
            return {
                "name": character_name,
                "description": base_info['base_description'],
                "detailed_description": f"{base_info['base_description']}, {base_info['default_traits']}",
                "physical_features": "",
                "costume": "",
                "distinctive_features": ""
            }
    
    def generate_character_reference_image(self, character_description: dict, output_path: str = None):
        """
        Generate a reference image for a character.
        
        Args:
            character_description: Dictionary with character description
            output_path: Optional path to save the image
        
        Returns:
            PIL Image object
        """
        # Build detailed prompt for character reference
        desc = character_description.get("detailed_description", character_description.get("description", ""))
        name = character_description.get("name", "character")
        
        prompt = f"""Character reference sheet: {name}, {desc}, 
full body character design, front view, clean background, 
comic book style, character sheet, reference image, 
vibrant colors, detailed, professional illustration"""
        
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
                        "negative_prompt": "blurry, low quality, distorted, text, watermark, multiple characters, background clutter",
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
                    
                    # Save if path provided
                    if output_path:
                        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                        image.save(output_path)
                    
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
                        print(f"Rate limit exceeded after {max_retries} attempts for character reference.")
                        return None
                else:
                    print(f"Replicate API error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None
                    
            except Exception as e:
                print(f"Error generating character reference image (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
        
        # If all retries failed
        return None
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay_between_requests:
            wait_time = self.min_delay_between_requests - time_since_last
            print(f"Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
    
    def generate_all_characters(self, character_names: list, story_context: str = "", save_references: bool = True):
        """
        Generate descriptions and reference images for all characters.
        
        Args:
            character_names: List of character names
            story_context: Story context for customization
            save_references: Whether to save reference images
        
        Returns:
            Dictionary mapping character names to their descriptions and images
        """
        characters = {}
        output_dir = "output/characters"
        
        if save_references:
            os.makedirs(output_dir, exist_ok=True)
        
        for char_name in character_names:
            print(f"  Generating character: {char_name}...")
            
            # Generate description
            char_desc = self.generate_character_description(char_name, story_context)
            
            # Generate reference image
            char_image = None
            if save_references:
                image_path = os.path.join(output_dir, f"{char_name}_reference.png")
                char_image = self.generate_character_reference_image(char_desc, image_path)
            
            characters[char_name] = {
                "description": char_desc,
                "reference_image": char_image,
                "reference_image_path": os.path.join(output_dir, f"{char_name}_reference.png") if save_references else None
            }
        
        return characters

