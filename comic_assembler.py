"""
Comic assembler module that combines panels into a final comic strip.
"""
from PIL import Image, ImageDraw, ImageFont
import os

class ComicAssembler:
    def __init__(self, panel_width: int = 800, panel_height: int = 600):
        """
        Initialize comic assembler.
        
        Args:
            panel_width: Width of each panel
            panel_height: Height of each panel
        """
        self.panel_width = panel_width
        self.panel_height = panel_height
        self.padding = 20
        self.panel_spacing = 30
    
    def assemble_comic(self, panel_images: list, panels_data: list, output_path: str = "output/comic.png"):
        """
        Assemble panels into a final comic strip.
        
        Args:
            panel_images: List of PIL Image objects
            panels_data: List of panel dictionaries with dialogue/narration
            output_path: Path to save final comic
        
        Returns:
            Path to generated comic
        """
        if not panel_images:
            raise ValueError("No panel images provided")
        
        # Resize all panels to consistent size
        resized_panels = []
        for img in panel_images:
            img_resized = img.resize((self.panel_width, self.panel_height), Image.Resampling.LANCZOS)
            resized_panels.append(img_resized)
        
        # Calculate total dimensions
        num_panels = len(resized_panels)
        total_width = self.panel_width + (2 * self.padding)
        total_height = (self.panel_height * num_panels) + (self.panel_spacing * (num_panels - 1)) + (2 * self.padding)
        
        # Create canvas
        comic = Image.new('RGB', (total_width, total_height), color='white')
        
        # Paste panels vertically
        y_offset = self.padding
        for i, panel_img in enumerate(resized_panels):
            # Add panel number label
            panel_with_label = self._add_panel_label(panel_img, i + 1)
            
            # Add dialogue/narration text if available
            if i < len(panels_data):
                panel_with_text = self._add_text_to_panel(panel_with_label, panels_data[i])
            else:
                panel_with_text = panel_with_label
            
            comic.paste(panel_with_text, (self.padding, y_offset))
            y_offset += self.panel_height + self.panel_spacing
        
        # Save comic
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        comic.save(output_path)
        print(f"Comic saved to {output_path}")
        return output_path
    
    def _add_panel_label(self, img: Image.Image, panel_num: int):
        """Add panel number label to image"""
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            font = ImageFont.load_default()
        
        label = f"Panel {panel_num}"
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw background rectangle
        padding = 5
        draw.rectangle(
            [(10, 10), (10 + text_width + 2*padding, 10 + text_height + 2*padding)],
            fill='white',
            outline='black',
            width=2
        )
        
        # Draw text
        draw.text((10 + padding, 10 + padding), label, fill='black', font=font)
        return img_copy
    
    def _add_text_to_panel(self, img: Image.Image, panel_data: dict):
        """Add dialogue/narration text to panel"""
        dialogue = panel_data.get("dialogue", "")
        narration = panel_data.get("narration", "")
        text = dialogue if dialogue else narration
        
        if not text:
            return img
        
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except:
            font = ImageFont.load_default()
        
        # Wrap text to fit panel width
        max_width = self.panel_width - 40
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
        
        # Draw text box at bottom
        line_height = 25
        text_box_height = len(lines) * line_height + 20
        text_y = self.panel_height - text_box_height - 10
        
        # Semi-transparent background
        overlay = Image.new('RGBA', (self.panel_width, text_box_height), (255, 255, 255, 200))
        img_copy.paste(overlay, (0, text_y), overlay)
        
        # Draw text
        for i, line in enumerate(lines):
            draw.text((20, text_y + 10 + i * line_height), line, fill='black', font=font)
        
        return img_copy

