"""
Text-to-Speech module for generating narration.
Uses OpenAI TTS API for high-quality voice generation.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class NarrationGenerator:
    def __init__(self, voice: str = "alloy"):
        """
        Initialize TTS generator.
        
        Args:
            voice: Voice type (alloy, echo, fable, onyx, nova, shimmer)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
        self.client = OpenAI(api_key=api_key)
        self.voice = voice
    
    def generate_narration_audio(self, text: str, output_path: str):
        """
        Generate audio file from narration text.
        
        Args:
            text: Narration text
            output_path: Path to save audio file
        
        Returns:
            Path to generated audio file
        """
        if not text or text.strip() == "":
            return None
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text
            )
            
            # Save audio file
            response.stream_to_file(output_path)
            return output_path
            
        except Exception as e:
            print(f"Error generating narration: {e}")
            return None
    
    def generate_all_narrations(self, panels: list, output_dir: str = "output/narration"):
        """
        Generate narration audio for all panels.
        
        Args:
            panels: List of panel dictionaries
            output_dir: Directory to save audio files
        
        Returns:
            List of audio file paths
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        audio_files = []
        for panel in panels:
            narration_text = panel.get("narration", "") or panel.get("dialogue", "")
            if narration_text:
                panel_num = panel.get("panel_number", len(audio_files) + 1)
                output_path = os.path.join(output_dir, f"panel_{panel_num}_narration.mp3")
                audio_file = self.generate_narration_audio(narration_text, output_path)
                if audio_file:
                    audio_files.append(audio_file)
        
        return audio_files

