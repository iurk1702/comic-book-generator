"""
Comic assembler module that combines panels into a final comic strip.
Supports PNG and PDF export formats.
"""
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import os
import io

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
    
    def assemble_comic_pdf(self, panel_images: list, panels_data: list, output_path: str = "output/comic.pdf"):
        """
        Assemble panels into a PDF comic book.
        
        Args:
            panel_images: List of PIL Image objects
            panels_data: List of panel dictionaries with dialogue/narration
            output_path: Path to save PDF file
        
        Returns:
            Path to generated PDF
        """
        if not panel_images:
            raise ValueError("No panel images provided")
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        page_width, page_height = letter
        
        # Resize panels for PDF (fit to page width with margins)
        margin = 40
        pdf_panel_width = page_width - (2 * margin)
        pdf_panel_height = (pdf_panel_width * self.panel_height) / self.panel_width
        
        y_position = page_height - margin - pdf_panel_height
        
        for i, panel_img in enumerate(panel_images):
            # Check if we need a new page
            if y_position < margin:
                c.showPage()
                y_position = page_height - margin - pdf_panel_height
            
            # Resize panel for PDF
            resized_panel = panel_img.resize((int(pdf_panel_width), int(pdf_panel_height)), Image.Resampling.LANCZOS)
            
            # Convert PIL Image to format reportlab can use
            img_buffer = io.BytesIO()
            resized_panel.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_reader = ImageReader(img_buffer)
            
            # Draw panel on PDF
            c.drawImage(img_reader, margin, y_position, width=pdf_panel_width, height=pdf_panel_height)
            
            # Add panel number
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin + 10, y_position + pdf_panel_height - 20, f"Panel {i + 1}")
            
            # Add narration/dialogue text if available
            if i < len(panels_data):
                panel_data = panels_data[i]
                text = panel_data.get("dialogue", "") or panel_data.get("narration", "")
                if text:
                    # Wrap text
                    text_width = pdf_panel_width - 20
                    words = text.split()
                    lines = []
                    current_line = []
                    
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if c.stringWidth(test_line, "Helvetica", 10) <= text_width:
                            current_line.append(word)
                        else:
                            if current_line:
                                lines.append(' '.join(current_line))
                            current_line = [word]
                    if current_line:
                        lines.append(' '.join(current_line))
                    
                    # Draw text box
                    text_height = len(lines) * 12 + 10
                    text_y = y_position - text_height - 5
                    
                    # Draw background
                    c.setFillColorRGB(1, 1, 1, alpha=0.8)
                    c.rect(margin, text_y, pdf_panel_width, text_height, fill=1, stroke=0)
                    
                    # Draw text
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont("Helvetica", 10)
                    for j, line in enumerate(lines):
                        c.drawString(margin + 10, text_y + text_height - (j + 1) * 12, line)
            
            # Move to next panel position
            y_position -= (pdf_panel_height + margin + 20)
        
        # Save PDF
        c.save()
        print(f"PDF saved to {output_path}")
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

