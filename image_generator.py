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
        # Using Google's nano-banana (Gemini 2.5 Flash Image) for better prompt adherence and character consistency
        # This model is specifically designed for character and style consistency across multiple images
        # Reference: https://replicate.com/google/nano-banana
        self.model = "google/nano-banana"  # Google's Gemini 2.5 Flash Image model
        # nano-banana supports both text-to-image and image-to-image natively
        self.img2img_model = "google/nano-banana"  # Same model supports img2img
        # IP-Adapter models for character consistency (try these in order)
        # These models embed reference images to maintain character consistency
        self.ip_adapter_models = [
            "lucataco/ip-adapter-plus",  # IP-Adapter Plus for better consistency
            "lucataco/ip-adapter-faceid",  # Face-specific IP-Adapter
            "lucataco/ip-adapter",  # Base IP-Adapter model
            "fofr/ip-adapter",  # Alternative IP-Adapter implementation
            "fofr/ip-adapter-plus",  # Alternative IP-Adapter Plus
        ]
        self.use_ip_adapter = True  # Enable IP-Adapter for character consistency
        self.ip_adapter_scale = 1.0  # How much reference images influence output (0.0-1.0) - 1.0 = maximum consistency
        self.ip_adapter_available = None  # Will be set to True/False after first attempt
        self.character_descriptions = {}  # Store character data (descriptions + reference images)
        # Rate limiting: 6 requests per minute = 10 seconds between requests
        self.min_delay_between_requests = 10  # seconds
        self.last_request_time = 0
        self.seed = None  # Seed for consistent generation across all panels
    
    def set_seed(self, seed: int = None):
        """
        Set seed for consistent image generation across all panels.
        If None, generates a random seed.
        
        Args:
            seed: Integer seed value (0 to 2^32-1). If None, generates random seed.
        """
        import random
        if seed is None:
            self.seed = random.randint(0, 2**32 - 1)
        else:
            self.seed = seed
        print(f"Using seed: {self.seed} for consistent character appearance")
    
    def set_character_descriptions(self, character_descriptions: dict):
        """Set character descriptions and reference images for consistent character appearance."""
        self.character_descriptions = character_descriptions
    
    def generate_panel_image(self, scene_description: str, panel_number: int, style: str = "comic book", characters_in_scene: list = None):
        """
        Generate an image for a comic panel with character consistency using image-to-image.
        
        Args:
            scene_description: Detailed scene description
            panel_number: Panel number for consistency
            style: Art style (default: comic book)
            characters_in_scene: List of character names appearing in this scene
        
        Returns:
            PIL Image object
        """
        # Get character reference images for image-to-image generation
        character_references = []
        character_names = []
        
        if characters_in_scene and self.character_descriptions:
            for char_name in characters_in_scene:
                if char_name in self.character_descriptions:
                    char_data = self.character_descriptions[char_name]
                    ref_image = char_data.get("reference_image")
                    if ref_image:
                        character_references.append(ref_image)
                        character_names.append(char_name)
        
        # Build character consistency prompt
        character_prompt = ""
        if characters_in_scene and self.character_descriptions:
            char_details = []
            for char_name in characters_in_scene:
                if char_name in self.character_descriptions:
                    char_data = self.character_descriptions[char_name]
                    char_desc = char_data.get('description', {})
                    if isinstance(char_desc, dict):
                        detailed = char_desc.get('detailed_description', char_desc.get('description', ''))
                    else:
                        detailed = str(char_desc)
                    if detailed:
                        char_details.append(f"{char_name}: {detailed}")
            
            if char_details:
                character_prompt = ", ".join(char_details) + ", "
        
        # Combine scene description with character consistency
        prompt = f"{character_prompt}{scene_description}, {style} style, vibrant colors, dynamic composition, comic book illustration, consistent character appearance"
        
        # Use IP-Adapter or image-to-image if we have character references
        if character_references and len(character_references) > 0:
            # Try IP-Adapter first for better multi-character consistency
            if self.use_ip_adapter and len(character_references) > 0:
                ip_result = self._generate_with_ip_adapter(prompt, character_references, character_names, panel_number, style)
                if ip_result:
                    return ip_result
                # If IP-Adapter fails, fall back to regular img2img
                print("IP-Adapter failed, falling back to image-to-image approach")
            
            # Fallback to regular image-to-image
            return self._generate_with_reference_images(prompt, character_references, character_names, panel_number, style)
        else:
            # Fallback to text-to-image
            return self._generate_text_to_image(prompt, panel_number, style)
    
    def _generate_with_reference_images(self, prompt: str, reference_images: list, character_names: list, panel_number: int, style: str):
        """
        Generate image using TRUE image-to-image with character reference images.
        Uses the reference image as input to the model for consistency.
        
        Args:
            prompt: Scene description prompt
            reference_images: List of PIL Image objects (character references)
            character_names: List of character names
            panel_number: Panel number
            style: Art style
        
        Returns:
            PIL Image object
        """
        # For multiple characters, create a composite reference image
        # This ensures ALL characters are considered, not just the first one
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        
        if len(reference_images) > 1:
            # Create a side-by-side composite of all character references
            composite_width = sum(img.width for img in reference_images)
            composite_height = max(img.height for img in reference_images)
            composite = Image.new('RGB', (composite_width, composite_height), (255, 255, 255))
            
            x_offset = 0
            for ref_img in reference_images:
                composite.paste(ref_img, (x_offset, 0))
                x_offset += ref_img.width
            
            # Save composite
            temp_ref_path = os.path.join(temp_dir, f"composite_ref_{panel_number}.png")
            composite.save(temp_ref_path)
            print(f"Using composite reference with {len(reference_images)} characters for image-to-image")
        else:
            # Single character - use their reference directly
            primary_reference = reference_images[0]
            primary_char = character_names[0] if character_names else "character"
            temp_ref_path = os.path.join(temp_dir, f"ref_{primary_char}_{panel_number}.png")
            primary_reference.save(temp_ref_path)
        
        # Enhanced prompt with ALL character details
        enhanced_prompt = prompt
        for char_name in character_names:
            if char_name in self.character_descriptions:
                char_data = self.character_descriptions[char_name]
                char_desc = char_data.get('description', {})
                if isinstance(char_desc, dict):
                    detailed = char_desc.get('detailed_description', char_desc.get('description', ''))
                else:
                    detailed = str(char_desc)
                enhanced_prompt += f", {char_name} must look exactly like: {detailed}, identical appearance, same costume colors and design, same facial features, consistent character design across all panels"
        
        try:
            # Rate limiting
            self._wait_for_rate_limit()
            
            # Retry logic
            max_retries = 3
            retry_delay = 5
            
            for attempt in range(max_retries):
                try:
                    # TRUE image-to-image: nano-banana supports native image input for character consistency
                    # Open image file for Replicate
                    with open(temp_ref_path, "rb") as img_file:
                        # nano-banana (Google Gemini 2.5 Flash Image) supports image input natively
                        # It's designed specifically for character and style consistency
                        try:
                            # Try nano-banana with image input (may not support this, will fallback)
                            input_params = {
                                "prompt": enhanced_prompt,
                                "image": img_file,
                                "width": 1024,  # 16:9 aspect ratio
                                "height": 576   # 16:9 aspect ratio (1024:576 = 16:9)
                            }
                            # Add seed if available (some models support it)
                            if self.seed is not None:
                                input_params["seed"] = self.seed
                            output = replicate.run(
                                self.img2img_model,
                                input=input_params
                            )
                        except (ReplicateError, Exception) as nano_error:
                            # Check if it's a rate limit error
                            if isinstance(nano_error, ReplicateError) and hasattr(nano_error, 'status') and nano_error.status == 429:
                                raise  # Re-raise to be handled by outer exception handler
                            
                            # If nano-banana doesn't support image input or fails, use SDXL img2img as fallback
                            print(f"nano-banana img2img failed, trying SDXL img2img: {nano_error}")
                            # Reopen file for SDXL
                            img_file.seek(0)
                            # Use SDXL with image input
                            sdxl_input = {
                                "prompt": enhanced_prompt,
                                "image": img_file,
                                "negative_prompt": "blurry, low quality, distorted, text, watermark, different character appearance",
                                "strength": 0.6,  # How much to follow the input image (0.0-1.0)
                                "guidance_scale": 7.5,
                                "num_inference_steps": 30,
                                "width": 1024,  # 16:9 aspect ratio
                                "height": 576   # 16:9 aspect ratio (1024:576 = 16:9)
                            }
                            # Add seed if available
                            if self.seed is not None:
                                sdxl_input["seed"] = self.seed
                            output = replicate.run(
                                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                                input=sdxl_input
                            )
                            
                    # Handle different output types from Replicate
                    # nano-banana returns FileOutput object, not a list or URL
                    if output:
                        # Check if it's a FileOutput object (has read() method or is file-like)
                        if hasattr(output, 'read'):
                            # FileOutput object - read directly
                            image = Image.open(output)
                            self.last_request_time = time.time()
                            return image
                        elif isinstance(output, list) and len(output) > 0:
                            # List of URLs or FileOutput objects
                            image_url = output[0]
                            if hasattr(image_url, 'read'):
                                image = Image.open(image_url)
                            else:
                                response = requests.get(str(image_url))
                                image = Image.open(io.BytesIO(response.content))
                            self.last_request_time = time.time()
                            return image
                        elif isinstance(output, str):
                            # URL string
                            response = requests.get(output)
                            image = Image.open(io.BytesIO(response.content))
                            self.last_request_time = time.time()
                            return image
                        else:
                            # Try to convert to string (URL) or iterate
                            try:
                                # FileOutput might be iterable
                                for item in output:
                                    if hasattr(item, 'read'):
                                        image = Image.open(item)
                                        self.last_request_time = time.time()
                                        return image
                                    else:
                                        response = requests.get(str(item))
                                        image = Image.open(io.BytesIO(response.content))
                                        self.last_request_time = time.time()
                                        return image
                            except (TypeError, StopIteration):
                                # Try as URL
                                response = requests.get(str(output))
                                image = Image.open(io.BytesIO(response.content))
                                self.last_request_time = time.time()
                                return image
                    else:
                        raise Exception("No image generated")
                        
                except ReplicateError as e:
                    # Check if model doesn't support image input - fallback to text-to-image
                    if "image" in str(e).lower() or "input" in str(e).lower() or "unexpected" in str(e).lower() or "parameter" in str(e).lower():
                        print(f"nano-banana may need different parameters, trying enhanced text-to-image approach...")
                        # nano-banana supports character consistency even with text-to-image
                        # Try using enhanced prompt approach
                        if attempt == max_retries - 1:  # Only on last attempt
                            # Try IP-Adapter with all reference images
                            ip_result = self._generate_with_ip_adapter(enhanced_prompt, reference_images, character_names, panel_number, style)
                            if ip_result:
                                return ip_result
                            # Fallback to enhanced text-to-image
                            return self._generate_text_to_image(enhanced_prompt, panel_number, style)
                    
                    if hasattr(e, 'status') and e.status == 429:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (2 ** attempt)
                            print(f"Rate limited. Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return self._create_placeholder(panel_number, "Rate limit exceeded")
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        return self._create_placeholder(panel_number, f"API error: {str(e)[:50]}")
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    # On last attempt, try fallback
                    if attempt == max_retries - 1:
                        # Try IP-Adapter with all reference images
                        ip_result = self._generate_with_ip_adapter(enhanced_prompt, reference_images, character_names, panel_number, style)
                        if ip_result:
                            return ip_result
                        # Final fallback to enhanced text-to-image
                        return self._generate_text_to_image(enhanced_prompt, panel_number, style)
                    return self._create_placeholder(panel_number, f"Generation failed: {str(e)[:50]}")
            
            # If all retries failed
            return self._create_placeholder(panel_number, "All retries failed")
                
        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def _generate_with_ip_adapter(self, prompt: str, reference_images: list, character_names: list, panel_number: int, style: str):
        """
        Generate image using IP-Adapter with multiple character reference images.
        IP-Adapter embeds reference images to maintain character consistency.
        
        Args:
            prompt: Scene description prompt
            reference_images: List of PIL Image objects (character references)
            character_names: List of character names
            panel_number: Panel number
            style: Art style
        
        Returns:
            PIL Image object or None if IP-Adapter fails
        """
        if not reference_images or len(reference_images) == 0:
            return None
        
        import tempfile
        import shutil
        
        # Check if IP-Adapter was previously determined to be unavailable
        if self.ip_adapter_available is False:
            return None
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        # Try each IP-Adapter model until one works
        for ip_model in self.ip_adapter_models:
            try:
                temp_dir = tempfile.mkdtemp()
                temp_ref_paths = []
                
                try:
                    # Save all reference images to temp files
                    for i, ref_img in enumerate(reference_images):
                        temp_path = os.path.join(temp_dir, f"ref_{i}.png")
                        ref_img.save(temp_path)
                        temp_ref_paths.append(temp_path)
                    
                    # Build input parameters for IP-Adapter
                    # IP-Adapter typically accepts:
                    # - prompt: text prompt
                    # - image: reference image(s)
                    # - scale: how much reference influences output (0.0-1.0)
                    # - num_outputs: number of images
                    
                    # For multiple characters, we can:
                    # 1. Composite all reference images into one (best for multi-character)
                    # 2. Use the first image (simple approach)
                    # 3. Use multiple images if model supports it
                    
                    # If multiple characters, create a composite reference image
                    if len(reference_images) > 1:
                        # Create a side-by-side composite of all character references
                        composite_width = sum(img.width for img in reference_images)
                        composite_height = max(img.height for img in reference_images)
                        composite = Image.new('RGB', (composite_width, composite_height), (255, 255, 255))
                        
                        x_offset = 0
                        for ref_img in reference_images:
                            composite.paste(ref_img, (x_offset, 0))
                            x_offset += ref_img.width
                        
                        # Save composite
                        composite_path = os.path.join(temp_dir, "composite_ref.png")
                        composite.save(composite_path)
                        ref_image_path = composite_path
                        print(f"Created composite reference with {len(reference_images)} characters")
                    else:
                        ref_image_path = temp_ref_paths[0]
                    
                    # Use reference image(s) with IP-Adapter
                    with open(ref_image_path, "rb") as img_file:
                        # Build input parameters - different models may use different parameter names
                        input_params = {
                            "prompt": prompt,
                            "image": img_file,
                            "scale": self.ip_adapter_scale,
                            "num_outputs": 1,
                            "width": 1024,  # 16:9 aspect ratio
                            "height": 576   # 16:9 aspect ratio (1024:576 = 16:9)
                        }
                        
                        # Some models use different parameter names
                        # Try common variations
                        if "faceid" in ip_model.lower():
                            # FaceID models might use different parameters
                            input_params["weight"] = self.ip_adapter_scale
                        
                        # Add seed if available
                        if self.seed is not None:
                            input_params["seed"] = self.seed
                        
                        # Try IP-Adapter model
                        try:
                            output = replicate.run(ip_model, input=input_params)
                        except Exception as param_error:
                            # If parameter error, try with minimal parameters
                            if "parameter" in str(param_error).lower() or "unexpected" in str(param_error).lower():
                                print(f"Trying {ip_model} with minimal parameters...")
                                minimal_params = {
                                    "prompt": prompt,
                                    "image": img_file
                                }
                                if self.seed is not None:
                                    minimal_params["seed"] = self.seed
                                output = replicate.run(ip_model, input=minimal_params)
                            else:
                                raise
                        
                        # Handle output
                        if output:
                            if hasattr(output, 'read'):
                                image = Image.open(output)
                            elif isinstance(output, list) and len(output) > 0:
                                item = output[0]
                                if hasattr(item, 'read'):
                                    image = Image.open(item)
                                else:
                                    response = requests.get(str(item))
                                    image = Image.open(io.BytesIO(response.content))
                            elif isinstance(output, str):
                                response = requests.get(str(output))
                                image = Image.open(io.BytesIO(response.content))
                            else:
                                # Try iterating
                                for item in output:
                                    if hasattr(item, 'read'):
                                        image = Image.open(item)
                                        break
                                    else:
                                        response = requests.get(str(item))
                                        image = Image.open(io.BytesIO(response.content))
                                        break
                            
                            self.last_request_time = time.time()
                            self.ip_adapter_available = True  # Mark as available
                            print(f"✓ IP-Adapter ({ip_model}) generated image successfully")
                            return image
                
                except (ReplicateError, Exception) as e:
                    # If this IP-Adapter model fails, try next one
                    if isinstance(e, ReplicateError) and hasattr(e, 'status'):
                        if e.status == 429:
                            # Rate limit - re-raise to be handled by outer retry logic
                            raise
                        elif e.status == 404:
                            # Model not found - mark as unavailable and skip
                            print(f"IP-Adapter model {ip_model} not found (404), skipping IP-Adapter")
                            self.ip_adapter_available = False
                            return None
                    print(f"IP-Adapter model {ip_model} failed: {e}, trying next model...")
                    continue
                
                finally:
                    # Clean up temp files
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except:
                        pass
                        
            except Exception as e:
                print(f"Error with IP-Adapter model {ip_model}: {e}")
                continue
        
        # If all IP-Adapter models failed, mark as unavailable and return None
        self.ip_adapter_available = False
        print("All IP-Adapter models failed, will use fallback method (image-to-image)")
        return None
    
    def _generate_text_to_image(self, prompt: str, panel_number: int, style: str):
        """
        Generate image using text-to-image with nano-banana or flux model.
        
        Args:
            prompt: Scene description prompt
            panel_number: Panel number
            style: Art style
        
        Returns:
            PIL Image object
        """
        
        # Rate limiting: ensure minimum delay between requests
        self._wait_for_rate_limit()
        
        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 5  # Start with 5 seconds
        
        for attempt in range(max_retries):
            try:
                # Try nano-banana model first with minimal parameters
                # nano-banana may not support all SDXL parameters
                try:
                    # nano-banana typically only needs prompt, but add 16:9 dimensions
                    # If model doesn't support width/height, it will ignore them
                    input_params = {
                        "prompt": prompt,
                        "width": 1024,  # 16:9 aspect ratio (1024:576 = 16:9)
                        "height": 576   # 16:9 aspect ratio
                    }
                    # Add seed if available (some models support it)
                    if self.seed is not None:
                        input_params["seed"] = self.seed
                    output = replicate.run(
                        self.model,
                        input=input_params
                    )
                except (ReplicateError, Exception) as model_error:
                    # Check if it's a rate limit error
                    if isinstance(model_error, ReplicateError) and hasattr(model_error, 'status') and model_error.status == 429:
                        raise  # Re-raise to be handled by outer exception handler
                    
                    # Fallback to SDXL if nano-banana fails for other reasons
                    print(f"nano-banana model failed, trying SDXL fallback: {model_error}")
                    sdxl_input = {
                        "prompt": prompt,
                        "negative_prompt": "blurry, low quality, distorted, text, watermark",
                        "num_outputs": 1,
                        "guidance_scale": 7.5,
                        "num_inference_steps": 30,
                        "width": 1024,  # 16:9 aspect ratio
                        "height": 576   # 16:9 aspect ratio (1024:576 = 16:9)
                    }
                    # Add seed if available
                    if self.seed is not None:
                        sdxl_input["seed"] = self.seed
                    output = replicate.run(
                        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                        input=sdxl_input
                    )
                
                # Handle different output types from Replicate
                # nano-banana returns FileOutput object, not a list or URL
                if output:
                    # Check if it's a FileOutput object (has read() method or is file-like)
                    if hasattr(output, 'read'):
                        # FileOutput object - read directly
                        image = Image.open(output)
                        self.last_request_time = time.time()
                        return image
                    elif isinstance(output, list) and len(output) > 0:
                        # List of URLs or FileOutput objects
                        image_url = output[0]
                        if hasattr(image_url, 'read'):
                            image = Image.open(image_url)
                        else:
                            response = requests.get(str(image_url))
                            image = Image.open(io.BytesIO(response.content))
                        self.last_request_time = time.time()
                        return image
                    elif isinstance(output, str):
                        # URL string
                        response = requests.get(output)
                        image = Image.open(io.BytesIO(response.content))
                        self.last_request_time = time.time()
                        return image
                    else:
                        # Try to convert to string (URL) or iterate
                        try:
                            # FileOutput might be iterable
                            for item in output:
                                if hasattr(item, 'read'):
                                    image = Image.open(item)
                                    self.last_request_time = time.time()
                                    return image
                                else:
                                    response = requests.get(str(item))
                                    image = Image.open(io.BytesIO(response.content))
                                    self.last_request_time = time.time()
                                    return image
                        except (TypeError, StopIteration):
                            # Try as URL
                            response = requests.get(str(output))
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

