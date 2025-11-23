"""
Video generator module for creating MP4 videos from comic panels with narration.
Each panel is shown with its corresponding narration audio.
"""
import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from PIL import Image
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
                    img_clip = ImageClip(temp_img_path, duration=duration)
                    img_clip = img_clip.set_fps(self.fps)
                    
                    # Add audio
                    audio_clip = AudioFileClip(audio_path)
                    video_clip = img_clip.set_audio(audio_clip)
                    
                else:
                    # No audio for this panel, show for minimum duration (3 seconds)
                    duration = 3.0
                    img_clip = ImageClip(temp_img_path, duration=duration)
                    img_clip = img_clip.set_fps(self.fps)
                    video_clip = img_clip
                
                video_clips.append(video_clip)
            
            # Concatenate all clips
            if len(video_clips) > 1:
                final_video = concatenate_videoclips(video_clips, method="compose")
            else:
                final_video = video_clips[0]
            
            # Write video file
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(temp_dir, 'temp_audio.m4a'),
                remove_temp=True,
                verbose=False,
                logger=None
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

