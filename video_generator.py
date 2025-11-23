"""
Video generator module for creating MP4 videos from comic pages with narration.
Each page is shown with all panels visible, and narrations play sequentially per panel.
"""
import os
# MoviePy 1.0.3 uses moviepy.editor for imports
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
except ImportError:
    # Fallback for MoviePy 2.x (if installed)
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
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
    
    def _distribute_panels_across_pages(self, total_panels: int, num_pages: int, avg_panels_per_page: float):
        """
        Distribute panels across pages with variation around average.
        Same logic as ComicAssembler.
        
        Args:
            total_panels: Total number of panels
            num_pages: Number of pages
            avg_panels_per_page: Average panels per page
        
        Returns:
            List of panel counts per page
        """
        import random
        
        target_total = int(num_pages * avg_panels_per_page)
        
        # If total_panels doesn't match target, adjust
        if total_panels != target_total:
            actual_avg = total_panels / num_pages
        else:
            actual_avg = avg_panels_per_page
        
        # Distribute panels with variation
        panels_per_page = []
        remaining_panels = total_panels
        
        for page_num in range(num_pages):
            if page_num == num_pages - 1:
                # Last page gets remaining panels
                panels_per_page.append(remaining_panels)
            else:
                # Calculate base number for this page
                base = int(actual_avg)
                
                # Add variation: -2 to +2 panels
                variation = random.randint(-2, 2)
                
                # Ensure we don't go below 1 or exceed remaining panels
                panels_this_page = max(1, min(base + variation, remaining_panels - (num_pages - page_num - 1)))
                
                # Ensure at least 1 panel per remaining page
                max_for_this_page = remaining_panels - (num_pages - page_num - 1)
                panels_this_page = min(panels_this_page, max_for_this_page)
                
                panels_per_page.append(panels_this_page)
                remaining_panels -= panels_this_page
        
        return panels_per_page
    
    def generate_video(self, panel_images: list, audio_files: list, panels_data: list, output_path: str = "output/comic.mp4", num_pages: int = 1, avg_panels_per_page: float = 5.0, assembler=None):
        """
        Generate a video from comic pages with narration.
        Each page shows all panels together, with narrations playing sequentially per panel.
        
        Args:
            panel_images: List of PIL Image objects for each panel
            audio_files: List of audio file paths (MP3) for each panel
            panels_data: List of panel dictionaries with metadata
            output_path: Path to save the video file
            num_pages: Number of pages in the comic
            avg_panels_per_page: Average panels per page (for distribution)
            assembler: ComicAssembler instance (to reuse layout logic)
        
        Returns:
            Path to generated video file
        """
        if not panel_images:
            raise ValueError("No panel images provided")
        
        if assembler is None:
            raise ValueError("ComicAssembler instance required")
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Get page layouts from assembler (already configured)
        layouts = assembler._generate_comic_layout(len(panel_images))
        
        if not layouts:
            raise ValueError("Failed to generate page layouts")
        
        # Create temporary directory for processed images
        temp_dir = tempfile.mkdtemp()
        processed_images = []
        
        try:
            video_clips = []
            all_audio_clips = []  # Keep all audio clips alive until video is written
            
            for page_num, page_layout in enumerate(layouts):
                # Create full page image with all panels (same as assembler.assemble_comic does)
                page_img = Image.new('RGB', (assembler.page_width, assembler.page_height), color='white')
                
                # Collect all panel indices and audio files for this page
                page_panel_indices = []
                page_audio_paths = []
                
                for panel_info in page_layout:
                    idx = panel_info["panel_index"]
                    if idx < len(panel_images):
                        page_panel_indices.append(idx)
                        
                        # Find audio file for this panel
                        panel_num = idx + 1
                        audio_path = None
                        for audio_file in audio_files:
                            if f"panel_{panel_num}_" in audio_file or f"panel_{idx+1}_" in audio_file:
                                audio_path = audio_file
                                break
                        page_audio_paths.append(audio_path)
                        
                        # Add dialogue/narration BEFORE resizing (so dialogue is part of panel)
                        panel_img = panel_images[idx]
                        if idx < len(panels_data):
                            panel_with_dialogue = assembler._add_text_to_panel(panel_img, panels_data[idx])
                        else:
                            panel_with_dialogue = panel_img
                        
                        # Resize panel (with dialogue) to fit layout size
                        # Use thumbnail to maintain aspect ratio, then paste on white background
                        panel_with_dialogue.thumbnail(
                            (panel_info["width"], panel_info["height"]),
                            Image.Resampling.LANCZOS
                        )
                        
                        # Create final panel with exact dimensions (centered if needed)
                        final_panel = Image.new('RGB', (panel_info["width"], panel_info["height"]), color='white')
                        paste_x = (panel_info["width"] - panel_with_dialogue.width) // 2
                        paste_y = (panel_info["height"] - panel_with_dialogue.height) // 2
                        final_panel.paste(panel_with_dialogue, (paste_x, paste_y))
                        
                        # Paste panel onto page
                        page_img.paste(final_panel, (panel_info["x"], panel_info["y"]))
                
                # Resize full page to video dimensions
                resized_page = self._resize_for_video(page_img)
                
                # Save full page image
                page_img_path = os.path.join(temp_dir, f"page_{page_num}.png")
                resized_page.save(page_img_path)
                processed_images.append(page_img_path)
                
                # Collect and concatenate all audio files for this page
                page_audio_clips = []
                total_duration = 0.0
                
                for audio_path in page_audio_paths:
                    if audio_path and os.path.exists(audio_path):
                        audio_clip = AudioFileClip(audio_path)
                        page_audio_clips.append(audio_clip)
                        total_duration += audio_clip.duration
                
                # Create video clip showing full page
                if page_audio_clips:
                    # Keep references to all audio clips to prevent garbage collection
                    all_audio_clips.extend(page_audio_clips)
                    
                    # Concatenate all narrations for this page sequentially
                    if len(page_audio_clips) > 1:
                        combined_audio = concatenate_audioclips(page_audio_clips)
                        all_audio_clips.append(combined_audio)  # Keep reference
                    else:
                        combined_audio = page_audio_clips[0]
                    
                    # Create video clip showing full page for duration of all narrations
                    page_clip = ImageClip(page_img_path, duration=total_duration)
                    # Handle both MoviePy 1.0.3 (set_audio) and 2.x (with_audio)
                    try:
                        # Try MoviePy 2.x API first
                        video_clip = page_clip.with_audio(combined_audio)
                    except AttributeError:
                        # Fallback to MoviePy 1.0.3 API
                        page_clip = page_clip.set_audio(combined_audio)
                        video_clip = page_clip
                else:
                    # No audio, show page for minimum duration
                    total_duration = max(3.0, len(page_panel_indices) * 2.0)  # At least 2 seconds per panel
                    page_clip = ImageClip(page_img_path, duration=total_duration)
                    video_clip = page_clip
                
                video_clips.append(video_clip)
            
            # Concatenate all clips
            if len(video_clips) > 1:
                final_video = concatenate_videoclips(video_clips, method="compose")
            else:
                final_video = video_clips[0]
            
            # Write video file
            # Handle both MoviePy 1.0.3 (verbose) and 2.x (logger)
            try:
                # Try MoviePy 2.x API first (logger parameter)
                try:
                    final_video.write_videofile(
                        output_path,
                        fps=self.fps,
                        codec='libx264',
                        audio_codec='aac',
                        temp_audiofile=os.path.join(temp_dir, 'temp_audio.m4a'),
                        remove_temp=True,
                        logger=None
                    )
                except TypeError:
                    # Fallback to MoviePy 1.0.3 API (verbose parameter)
                    final_video.write_videofile(
                        output_path,
                        fps=self.fps,
                        codec='libx264',
                        audio_codec='aac',
                        temp_audiofile=os.path.join(temp_dir, 'temp_audio.m4a'),
                        remove_temp=True,
                        verbose=False
                    )
            finally:
                # Clean up AFTER video is written - clips must stay open during writing
                try:
                    final_video.close()
                except:
                    pass
                for clip in video_clips:
                    try:
                        clip.close()
                    except:
                        pass
                # Close all audio clips
                for audio_clip in all_audio_clips:
                    try:
                        audio_clip.close()
                    except:
                        pass
            
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
        Add dialogue/narration text to panel image for video with character name formatting.
        
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
            font_size = int(self.video_height * 0.04)  # ~43px for 1080p
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            bold_font = ImageFont.truetype("/System/Library/Fonts/Helvetica-Bold.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
                bold_font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 40)
            except:
                font = ImageFont.load_default()
                bold_font = font
        
        # Parse dialogues: "Character1: dialogue1 | Character2: dialogue2"
        dialogues = []
        if " | " in text:
            # Multiple dialogues
            dialogue_parts = text.split(" | ")
            for part in dialogue_parts:
                if ":" in part:
                    char_name, dialogue_text = part.split(":", 1)
                    dialogues.append({"character": char_name.strip(), "dialogue": dialogue_text.strip()})
                else:
                    dialogues.append({"character": "", "dialogue": part.strip()})
        elif ":" in text:
            # Single dialogue with character name
            char_name, dialogue_text = text.split(":", 1)
            dialogues.append({"character": char_name.strip(), "dialogue": dialogue_text.strip()})
        else:
            # No character name, treat as narration
            dialogues.append({"character": "", "dialogue": text})
        
        # Build formatted text lines with character names
        max_width = self.video_width - 80
        lines = []
        
        for dialogue_item in dialogues:
            char_name = dialogue_item["character"]
            dialogue_text = dialogue_item["dialogue"]
            
            if char_name:
                # Format: "CharacterName: dialogue"
                full_text = f"{char_name}: {dialogue_text}"
            else:
                full_text = dialogue_text
            
            # Wrap text to fit video width
            words = full_text.split()
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
        overlay = Image.new('RGBA', (self.video_width, text_box_height), (0, 0, 0, 180))
        img_copy.paste(overlay, (0, text_y), overlay)
        
        # Draw text with character names in bold (white for visibility)
        text_x = 40
        for i, line in enumerate(lines):
            x_pos = text_x
            # Check if line has character name
            if ":" in line:
                char_part, dialogue_part = line.split(":", 1)
                # Draw character name in bold
                draw.text((x_pos, text_y + 20 + i * line_height), char_part + ":", fill='white', font=bold_font)
                # Measure character name width
                char_bbox = draw.textbbox((0, 0), char_part + ":", font=bold_font)
                x_pos = char_bbox[2] - char_bbox[0] + text_x
                # Draw dialogue text
                draw.text((x_pos, text_y + 20 + i * line_height), dialogue_part, fill='white', font=font)
            else:
                # No character name, just draw line
                draw.text((x_pos, text_y + 20 + i * line_height), line, fill='white', font=font)
        
        return img_copy

