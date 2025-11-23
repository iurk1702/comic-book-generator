"""
LLM module for generating comic book stories.
Generates a short story and splits it into 3-5 panels with descriptions.
"""
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Predefined characters for v1 (kept for backward compatibility)
PREDEFINED_CHARACTERS = {
    "hero": "A brave superhero with a cape",
    "villain": "A menacing villain with dark powers",
    "sidekick": "A loyal companion with special abilities"
}

class StoryGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
        self.client = OpenAI(api_key=api_key)
    
    def generate_story(self, user_prompt: str, num_panels: int = 4, characters: list = None, character_descriptions: dict = None):
        """
        Generate a comic story split into panels.
        
        Args:
            user_prompt: User's story idea
            num_panels: Number of panels (3-5)
            characters: List of character names to use
            character_descriptions: Dictionary of character descriptions for consistency
        
        Returns:
            List of panel dictionaries with 'scene_description' and 'dialogue'
        """
        if characters is None:
            characters = ["hero", "villain"]
        
        # Build character context with detailed descriptions if available
        if character_descriptions:
            char_context = "\n".join([
                f"- {char}: {character_descriptions[char]['description'].get('detailed_description', character_descriptions[char]['description'].get('description', PREDEFINED_CHARACTERS.get(char, 'A character')))}"
                for char in characters if char in character_descriptions
            ])
        else:
            char_context = "\n".join([f"- {char}: {PREDEFINED_CHARACTERS.get(char, 'A character')}" 
                                      for char in characters])
        
        # Build character names list for dialogue formatting
        character_names_list = []
        if character_descriptions:
            character_names_list = [char_data.get("name", char) for char, char_data in character_descriptions.items() if char in characters]
        elif characters:
            character_names_list = characters
        
        char_names_str = ", ".join(character_names_list) if character_names_list else "characters"
        
        system_prompt = f"""You are a comic book story generator. Generate a short, engaging story split into exactly {num_panels} panels.

Available characters:
{char_context}

Character names for dialogues: {char_names_str}

IMPORTANT DIALOGUE FORMATTING RULES:
- All dialogues MUST be formatted as "CharacterName: dialogue text"
- If multiple characters speak in one panel, separate dialogues with " | " (space pipe space)
- Example: "Iron Man: I'll save the day! | Captain America: Not without me!"
- Each dialogue must be preceded by the character's name followed by a colon
- Use character names exactly as provided: {char_names_str}
- If no character speaks, leave dialogue empty

For each panel, provide:
1. A detailed visual scene description (for image generation)
2. Dialogue text formatted as "CharacterName: dialogue" (multiple separated by " | ")
3. Narration text (if any, for narrator)

Format your response as a JSON array with {num_panels} objects, each with:
- "panel_number": panel number (1-{num_panels})
- "scene_description": detailed visual description for image generation
- "dialogue": dialogue text formatted as "CharacterName: dialogue" (can be empty, multiple separated by " | ")
- "narration": narration text for this panel (if any, for narrator voice)

Keep the story simple, visual, and suitable for a comic book format."""

        user_message = f"Create a comic story about: {user_prompt}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using cheaper model for v1
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.8
            )
            
            # Parse response - try to extract JSON from markdown code blocks or plain JSON
            content = response.choices[0].message.content
            
            # Try to extract JSON from markdown code blocks (array or object)
            json_match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Try to find JSON array or object in content
                json_match = re.search(r'(\[.*?\]|\{.*?\})', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            try:
                story_data = json.loads(content)
                
                # Extract panels
                if isinstance(story_data, list):
                    panels = story_data
                elif "panels" in story_data:
                    panels = story_data["panels"]
                elif isinstance(story_data, dict):
                    # Single panel object
                    panels = [story_data]
                else:
                    raise ValueError("Unexpected response format")
                
                # Ensure all panels have required fields
                for panel in panels:
                    if "panel_number" not in panel:
                        panel["panel_number"] = panels.index(panel) + 1
                    if "scene_description" not in panel:
                        panel["scene_description"] = "A comic book scene"
                    if "dialogue" not in panel:
                        panel["dialogue"] = ""
                    if "narration" not in panel:
                        panel["narration"] = panel.get("dialogue", "")
                
                return panels[:num_panels]  # Ensure we don't exceed num_panels
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Could not parse JSON response: {e}")
                # If JSON parsing fails, parse text response
                return self._parse_text_response(content, num_panels)
            
        except Exception as e:
            print(f"Error generating story: {e}")
            # Return a simple fallback story
            return self._generate_fallback_story(num_panels, user_prompt)
    
    def _parse_text_response(self, text: str, num_panels: int):
        """Parse text response if JSON parsing fails"""
        panels = []
        # Simple parsing - split by panel markers
        panel_sections = re.split(r'[Pp]anel\s*\d+', text)
        for i in range(min(num_panels, len(panel_sections))):
            section = panel_sections[i] if i < len(panel_sections) else ""
            panels.append({
                "panel_number": i + 1,
                "scene_description": section[:200] if section else f"A scene related to the story",
                "dialogue": "",
                "narration": section[:100] if section else f"Panel {i+1} narration"
            })
        return panels[:num_panels]
    
    def _generate_fallback_story(self, num_panels: int, prompt: str):
        """Fallback story if API fails"""
        panels = []
        for i in range(num_panels):
            panels.append({
                "panel_number": i + 1,
                "scene_description": f"Panel {i+1}: A scene related to {prompt}",
                "dialogue": "",
                "narration": f"This is panel {i+1} of the story about {prompt}"
            })
        return panels

