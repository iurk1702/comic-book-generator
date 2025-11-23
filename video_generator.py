"""
Video generator module for creating MP4 videos from comic panels with narration.
Each panel is shown with its corresponding narration audio.
"""
import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import tempfile

class VideoGenerator:
    def __init__(self, video_width: int = 1920, video_height: int = 1080, fps: int = 24):
        """
        Initialize video generator.
        
        Args:
            video_width: Width of output video (default: 1920 for HD)
            video_height: Height of output video (default: 1080 for HD)
            fps: Frames per second (default: 24)
        """
        self.video_width = video_width
        self.video_height = video_height
        self.fps = fps
    
    def generate_video(self, panel_images: list, audio_files: list, panels_data: list, output_path: str = "output/comic.mp4"):
        """
        Generate a video from comic panels with narration.
        
        Args:
            panel_images: List of PIL Image objects for each panel
            audio_files: List of audio file paths (MP3) for each panel
            panels_data: List of panel dictionaries with metadata
            output_path: Path to save the video file
        
        Returns:
            Path to generated video file
        """
        if not panel_images:
            raise ValueError("No panel images provided")
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Create temporary directory for processed images
        temp_dir = tempfile.mkdtemp()
        processed_images = []
        
        try:
            # Process each panel
            video_clips = []
            
            for i, panel_img in enumerate(panel_images):
                panel_num = i + 1
                
                # Resize panel to video dimensions (maintain aspect ratio, center with black bars if needed)
                resized_img = self._resize_for_video(panel_img)
                
                # Add dialogue/narration text to panel if available
                if i < len(panels_data):
                    resized_img = self._add_text_to_panel(resized_img, panels_data[i])
                
                # Save to temporary file
                temp_img_path = os.path.join(temp_dir, f"panel_{panel_num}.png")
                resized_img.save(temp_img_path)
                processed_images.append(temp_img_path)
                
                # Find corresponding audio file
                audio_path = None
                # Try to match audio file by panel number
                for audio_file in audio_files:
                    # Match by panel number in filename
                    if f"panel_{panel_num}_" in audio_file or f"panel_{i+1}_" in audio_file:
                        audio_path = audio_file
                        break
                
                # Create video clip for this panel
                if audio_path and os.path.exists(audio_path):
                    # Get audio duration
                    audio_clip = AudioFileClip(audio_path)
                    duration = audio_clip.duration
                    audio_clip.close()
                    
                    # Create image clip with audio duration
                    # In MoviePy 2.x, fps is set at write time, not on the clip
                    img_clip = ImageClip(temp_img_path, duration=duration)
                    
                    # Add audio (MoviePy 2.x uses with_audio instead of set_audio)
                    audio_clip = AudioFileClip(audio_path)
                    video_clip = img_clip.with_audio(audio_clip)
                    
                else:
                    # No audio for this panel, show for minimum duration (3 seconds)
                    duration = 3.0
                    img_clip = ImageClip(temp_img_path, duration=duration)
                    video_clip = img_clip
                
                video_clips.append(video_clip)
            
            # Concatenate all clips
            if len(video_clips) > 1:
                final_video = concatenate_videoclips(video_clips, method="compose")
            else:
                final_video = video_clips[0]
            
            # Write video file
            # MoviePy 2.x API: verbose parameter removed, logger accepts 'bar' or None
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(temp_dir, 'temp_audio.m4a'),
                remove_temp=True,
                logger=None  # None = no progress bar, 'bar' = show progress bar
            )
            
            # Clean up
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            print(f"Video saved to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating video: {e}")
            raise
        finally:
            # Clean up temporary files
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def _resize_for_video(self, img: Image.Image):
        """
        Resize image to fit video dimensions while maintaining aspect ratio.
        Adds black bars if needed to maintain aspect ratio.
        
        Args:
            img: PIL Image object
        
        Returns:
            Resized PIL Image with black bars if needed
        """
        # Calculate scaling to fit within video dimensions
        img_width, img_height = img.size
        scale_w = self.video_width / img_width
        scale_h = self.video_height / img_height
        scale = min(scale_w, scale_h)  # Use smaller scale to fit within bounds
        
        # Resize image
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create black background
        final_img = Image.new('RGB', (self.video_width, self.video_height), color='black')
        
        # Center the resized image
        x_offset = (self.video_width - new_width) // 2
        y_offset = (self.video_height - new_height) // 2
        final_img.paste(resized_img, (x_offset, y_offset))
        
        return final_img
    
    def _add_text_to_panel(self, img: Image.Image, panel_data: dict):
        """
        Add dialogue/narration text to panel image for video.
        
        Args:
            img: PIL Image object (already resized for video)
            panel_data: Dictionary with dialogue/narration text
        
        Returns:
            PIL Image with text overlay
        """
        dialogue = panel_data.get("dialogue", "")
        narration = panel_data.get("narration", "")
        text = dialogue if dialogue else narration
        
        if not text:
            return img
        
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Use larger font for video (HD resolution)
        try:
            # Try to use a larger, readable font
            font_size = int(self.video_height * 0.04)  # ~43px for 1080p
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font = ImageFont.load_default()
        
        # Wrap text to fit video width (with margins)
        max_width = self.video_width - 80  # Margins
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text box at bottom of video
        line_height = int(self.video_height * 0.05)  # ~54px for 1080p
        text_box_height = len(lines) * line_height + 40
        text_y = self.video_height - text_box_height - 20
        
        # Create semi-transparent background overlay
        overlay = Image.new('RGBA', (self.video_width, text_box_height), (0, 0, 0, 180))  # Dark semi-transparent
        img_copy.paste(overlay, (0, text_y), overlay)
        
        # Draw text (white for better visibility on dark background)
        text_x = 40  # Left margin
        for i, line in enumerate(lines):
            draw.text((text_x, text_y + 20 + i * line_height), line, fill='white', font=font)
        
        return img_copy

