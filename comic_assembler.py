"""
Comic assembler module that combines panels into a final comic strip.
Supports PNG and PDF export formats.
Includes speech bubble rendering with character positioning.
"""
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import os
import io
import numpy as np

# Try to import face detection using OpenCV (more compatible than MediaPipe)
FACE_DETECTION_AVAILABLE = False
try:
    import cv2
    FACE_DETECTION_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    # OpenCV not available - will use fixed positions for speech bubbles
    FACE_DETECTION_AVAILABLE = False
    print("Note: opencv-python not available. Speech bubbles will use fixed positions.")

class ComicAssembler:
    def __init__(self, panel_width: int = 640, panel_height: int = 360, page_width: int = 1920, page_height: int = 1080):
        """
        Initialize comic assembler.
         
        Args:
            panel_width: Base width of each panel (for single panels) - 16:9 aspect ratio
            panel_height: Base height of each panel (for single panels) - 16:9 aspect ratio
            page_width: Width of comic page (for multi-panel layouts) - 16:9 (1920×1080)
            page_height: Height of comic page (for multi-panel layouts) - 16:9 (1920×1080)
        """
        self.panel_width = panel_width
        self.panel_height = panel_height
        self.page_width = page_width  # Full page width for multi-panel layouts (16:9)
        self.page_height = page_height  # Full page height for multi-panel layouts (16:9)
        self.padding = 40  # Page margins
        self.panel_spacing = 15  # Space between panels
        self.gutter = 10  # Space between panels in grid
    
    def set_page_config(self, num_pages: int, avg_panels_per_page: float):
        """
        Set page configuration for comic book.
        
        Args:
            num_pages: Total number of pages
            avg_panels_per_page: Average number of panels per page
        """
        self.num_pages = num_pages
        self.avg_panels_per_page = avg_panels_per_page
    
    def _distribute_panels_across_pages(self, total_panels: int):
        """
        Distribute panels across pages with variation around average.
        Ensures total panels match and each page has reasonable variation.
        
        Args:
            total_panels: Total number of panels to distribute
        
        Returns:
            List of panel counts per page
        """
        if not self.num_pages or not hasattr(self, 'avg_panels_per_page'):
            # Fallback: use old method
            return None
        
        import random
        
        target_total = int(self.num_pages * self.avg_panels_per_page)
        
        # If total_panels doesn't match target, adjust
        if total_panels != target_total:
            # Use actual total_panels, recalculate average
            actual_avg = total_panels / self.num_pages
        else:
            actual_avg = self.avg_panels_per_page
        
        # Distribute panels with variation
        panels_per_page = []
        remaining_panels = total_panels
        
        for page_num in range(self.num_pages):
            if page_num == self.num_pages - 1:
                # Last page gets remaining panels
                panels_per_page.append(remaining_panels)
            else:
                # Calculate base number for this page
                base = int(actual_avg)
                
                # Add variation: -2 to +2 panels (or more if needed)
                variation = random.randint(-2, 2)
                
                # Ensure we don't go below 1 or exceed remaining panels
                panels_this_page = max(1, min(base + variation, remaining_panels - (self.num_pages - page_num - 1)))
                
                # Ensure at least 1 panel per remaining page
                max_for_this_page = remaining_panels - (self.num_pages - page_num - 1)
                panels_this_page = min(panels_this_page, max_for_this_page)
                
                panels_per_page.append(panels_this_page)
                remaining_panels -= panels_this_page
        
        return panels_per_page
    
    def _generate_comic_layout(self, num_panels: int):
        """
        Generate a comic book layout with multiple panels per page and variable sizes.
        Creates layouts similar to real comic books.
        
        Args:
            num_panels: Total number of panels to arrange
        
        Returns:
            List of page layouts, each containing list of panel positions and sizes
        """
        layouts = []
        
        if num_panels <= 0:
            return layouts
        
        # Distribute panels across pages if page config is set
        if self.num_pages and hasattr(self, 'avg_panels_per_page'):
            panels_per_page = self._distribute_panels_across_pages(num_panels)
            panel_start_idx = 0
            
            for page_num, panels_on_page in enumerate(panels_per_page):
                page_layout = self._generate_page_layout(panels_on_page, panel_start_idx)
                layouts.append(page_layout)
                panel_start_idx += panels_on_page
        else:
            # Old method: single page or auto-distribute
            if num_panels <= 9:
                # Single page
                page_layout = self._generate_page_layout(num_panels, 0)
                layouts.append(page_layout)
            else:
                # Multiple pages: 6 panels per page
                panels_per_page = 6
                num_pages = (num_panels + panels_per_page - 1) // panels_per_page
                panel_start_idx = 0
                
                for page_num in range(num_pages):
                    panels_on_page = min(panels_per_page, num_panels - panel_start_idx)
                    page_layout = self._generate_page_layout(panels_on_page, panel_start_idx)
                    layouts.append(page_layout)
                    panel_start_idx += panels_on_page
        
        return layouts
    
    def _generate_page_layout(self, num_panels_on_page: int, start_panel_index: int):
        """
        Generate layout for a single page with specified number of panels.
        
        Args:
            num_panels_on_page: Number of panels on this page
            start_panel_index: Starting index for panel numbering
        
        Returns:
            List of panel positions and sizes for this page
        """
        # Available content area (excluding margins)
        content_width = self.page_width - (2 * self.padding)
        content_height = self.page_height - (2 * self.padding)
        
        page_layout = []
        
        # Common comic layouts based on number of panels on this page
        if num_panels_on_page <= 3:
            # 1-3 panels: Simple vertical layout
            panel_width = content_width
            panel_height = content_height // num_panels_on_page - (self.gutter * (num_panels_on_page - 1))
            
            y_pos = self.padding
            for i in range(num_panels_on_page):
                page_layout.append({
                    "x": self.padding,
                    "y": y_pos,
                    "width": panel_width,
                    "height": panel_height,
                    "panel_index": start_panel_index + i
                })
                y_pos += panel_height + self.gutter
                
        elif num_panels_on_page == 4:
            # 4 panels: 2x2 grid
            panel_width = (content_width - self.gutter) // 2
            panel_height = (content_height - self.gutter) // 2
            
            for row in range(2):
                for col in range(2):
                    idx = row * 2 + col
                    if idx < num_panels_on_page:
                        page_layout.append({
                            "x": self.padding + col * (panel_width + self.gutter),
                            "y": self.padding + row * (panel_height + self.gutter),
                            "width": panel_width,
                            "height": panel_height,
                            "panel_index": start_panel_index + idx
                        })
                        
        elif num_panels_on_page == 5:
            # 5 panels: 3 on top (smaller), 2 on bottom (larger)
            top_panel_width = (content_width - 2 * self.gutter) // 3
            top_panel_height = (content_height - self.gutter) // 3
            bottom_panel_width = (content_width - self.gutter) // 2
            bottom_panel_height = (content_height - self.gutter) * 2 // 3
            
            # Top row: 3 panels
            for i in range(3):
                page_layout.append({
                    "x": self.padding + i * (top_panel_width + self.gutter),
                    "y": self.padding,
                    "width": top_panel_width,
                    "height": top_panel_height,
                    "panel_index": start_panel_index + i
                })
            # Bottom row: 2 larger panels
            for i in range(2):
                page_layout.append({
                    "x": self.padding + i * (bottom_panel_width + self.gutter),
                    "y": self.padding + top_panel_height + self.gutter,
                    "width": bottom_panel_width,
                    "height": bottom_panel_height,
                    "panel_index": start_panel_index + 3 + i
                })
                
        elif num_panels_on_page == 6:
            # 6 panels: 3x2 grid
            panel_width = (content_width - 2 * self.gutter) // 3
            panel_height = (content_height - self.gutter) // 2
            
            for row in range(2):
                for col in range(3):
                    idx = row * 3 + col
                    if idx < num_panels_on_page:
                        page_layout.append({
                            "x": self.padding + col * (panel_width + self.gutter),
                            "y": self.padding + row * (panel_height + self.gutter),
                            "width": panel_width,
                            "height": panel_height,
                            "panel_index": start_panel_index + idx
                        })
                        
        elif num_panels_on_page == 9:
            # 9 panels: 3x3 grid
            panel_width = (content_width - 2 * self.gutter) // 3
            panel_height = (content_height - 2 * self.gutter) // 3
            
            for row in range(3):
                for col in range(3):
                    idx = row * 3 + col
                    if idx < num_panels_on_page:
                        page_layout.append({
                            "x": self.padding + col * (panel_width + self.gutter),
                            "y": self.padding + row * (panel_height + self.gutter),
                            "width": panel_width,
                            "height": panel_height,
                            "panel_index": start_panel_index + idx
                        })
        else:
            # For other numbers: use flexible grid
            # Try to fit in a reasonable grid
            cols = 3
            rows = (num_panels_on_page + cols - 1) // cols
            if rows > 3:
                rows = 3
                cols = (num_panels_on_page + rows - 1) // rows
            
            panel_width = (content_width - (cols - 1) * self.gutter) // cols
            panel_height = (content_height - (rows - 1) * self.gutter) // rows
            
            for i in range(num_panels_on_page):
                row = i // cols
                col = i % cols
                if row < rows:
                    page_layout.append({
                        "x": self.padding + col * (panel_width + self.gutter),
                        "y": self.padding + row * (panel_height + self.gutter),
                        "width": panel_width,
                        "height": panel_height,
                        "panel_index": start_panel_index + i
                    })
        
        return page_layout
    
    def assemble_comic(self, panel_images: list, panels_data: list, output_path: str = "output/comic.png"):
        """
        Assemble panels into a final comic with multi-panel pages and variable sizes.
        
        Args:
            panel_images: List of PIL Image objects
            panels_data: List of panel dictionaries with dialogue/narration
            output_path: Path to save final comic
        
        Returns:
            Path to generated comic
        """
        if not panel_images:
            raise ValueError("No panel images provided")
        
        # Generate layout for all panels
        layouts = self._generate_comic_layout(len(panel_images))
        
        if not layouts:
            raise ValueError("Failed to generate layout")
        
        # If single page, create that page; if multiple pages, create multi-page image
        if len(layouts) == 1:
            # Single page comic
            page_layout = layouts[0]
            comic = Image.new('RGB', (self.page_width, self.page_height), color='white')
            
            for panel_info in page_layout:
                idx = panel_info["panel_index"]
                if idx < len(panel_images):
                    panel_img = panel_images[idx]
                    
                    # Add dialogue/narration BEFORE resizing (so dialogue is part of panel)
                    if idx < len(panels_data):
                        panel_with_dialogue = self._add_text_to_panel(panel_img, panels_data[idx])
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
                    
                    # Paste panel at calculated position
                    comic.paste(final_panel, (panel_info["x"], panel_info["y"]))
            
            # Save comic
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            comic.save(output_path)
            print(f"Comic saved to {output_path}")
            return output_path
        else:
            # Multiple pages: create vertical strip (for PNG, PDF handles pages separately)
            total_height = len(layouts) * self.page_height + (len(layouts) - 1) * 50  # 50px gap between pages
            comic = Image.new('RGB', (self.page_width, total_height), color='white')
            
            y_offset = 0
            for page_num, page_layout in enumerate(layouts):
                # Create page
                page_img = Image.new('RGB', (self.page_width, self.page_height), color='white')
                
                for panel_info in page_layout:
                    idx = panel_info["panel_index"]
                    if idx < len(panel_images):
                        panel_img = panel_images[idx]
                        
                        # Add dialogue/narration BEFORE resizing (so dialogue is part of panel)
                        if idx < len(panels_data):
                            panel_with_dialogue = self._add_text_to_panel(panel_img, panels_data[idx])
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
                        
                        # Paste panel
                        page_img.paste(final_panel, (panel_info["x"], panel_info["y"]))
                
                # Paste page into comic
                comic.paste(page_img, (0, y_offset))
                y_offset += self.page_height + 50
            
            # Save comic
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            comic.save(output_path)
            print(f"Comic saved to {output_path}")
            return output_path
    
    def assemble_comic_pdf(self, panel_images: list, panels_data: list, output_path: str = "output/comic.pdf"):
        """
        Assemble panels into a PDF comic book with multi-panel pages.
        
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
        
        # Generate layout for all panels
        layouts = self._generate_comic_layout(len(panel_images))
        
        if not layouts:
            raise ValueError("Failed to generate layout")
        
        # Scale layout to PDF page size
        scale_x = page_width / self.page_width
        scale_y = page_height / self.page_height
        
        # Render each page
        for page_num, page_layout in enumerate(layouts):
            if page_num > 0:
                c.showPage()  # New page
            
            # Draw each panel on this page
            for panel_info in page_layout:
                idx = panel_info["panel_index"]
                if idx < len(panel_images):
                    panel_img = panel_images[idx]
                    
                    # Add dialogue/narration BEFORE resizing (so dialogue is part of panel)
                    if idx < len(panels_data):
                        panel_with_dialogue = self._add_text_to_panel(panel_img, panels_data[idx])
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
                    
                    # Scale panel position and size to PDF coordinates
                    pdf_x = panel_info["x"] * scale_x
                    pdf_y = page_height - (panel_info["y"] * scale_y) - (panel_info["height"] * scale_y)  # Flip Y axis
                    pdf_width = panel_info["width"] * scale_x
                    pdf_height = panel_info["height"] * scale_y
                    
                    # Use final_panel (already resized with dialogue)
                    panel_with_text = final_panel
                    
                    # Convert PIL Image to format reportlab can use
                    img_buffer = io.BytesIO()
                    panel_with_text.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    img_reader = ImageReader(img_buffer)
                    
                    # Draw panel on PDF
                    c.drawImage(img_reader, pdf_x, pdf_y, width=pdf_width, height=pdf_height)
        
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
        """Add dialogue/narration text to panel with speech bubbles pointing to characters"""
        dialogue = panel_data.get("dialogue", "")
        narration = panel_data.get("narration", "")
        text = dialogue if dialogue else narration
        
        if not text:
            return img
        
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
        
        # Add dialogues below panel (ordered by character speech)
        if dialogues and dialogues[0].get("character"):
            return self._add_dialogues_below_panel(img, dialogues)
        else:
            return self._add_narration_text(img, text)
    
    def _add_dialogues_below_panel(self, img: Image.Image, dialogues: list):
        """Add dialogues below panel, ordered by character speech"""
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Get actual image dimensions
        img_width, img_height = img.size
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            bold_font = ImageFont.truetype("/System/Library/Fonts/Helvetica-Bold.ttc", 14)
        except:
            font = ImageFont.load_default()
            bold_font = font
        
        # Build dialogue text lines (in order of speech)
        dialogue_lines = []
        for dialogue_item in dialogues:
            char_name = dialogue_item.get("character", "").strip()
            dialogue_text = dialogue_item.get("dialogue", "").strip()
            
            if char_name and dialogue_text:
                # Format: "Character name: dialogue"
                dialogue_lines.append(f"{char_name}: {dialogue_text}")
            elif dialogue_text:
                # No character name, just dialogue
                dialogue_lines.append(dialogue_text)
        
        if not dialogue_lines:
            return img_copy
        
        # Calculate text dimensions and wrap text
        padding = 10
        max_text_width = img_width - (2 * padding)
        wrapped_lines = []
        
        for line in dialogue_lines:
            words = line.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_text_width:
                    current_line.append(word)
                else:
                    if current_line:
                        wrapped_lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                wrapped_lines.append(' '.join(current_line))
        
        # Calculate text box height
        line_height = 18
        text_box_height = len(wrapped_lines) * line_height + (2 * padding)
        
        # Create new image with space for dialogue at bottom
        new_height = img_height + text_box_height
        new_img = Image.new('RGB', (img_width, new_height), color='white')
        new_img.paste(img_copy, (0, 0))  # Paste original panel at top
        
        # Draw text box background
        draw_new = ImageDraw.Draw(new_img)
        text_y = img_height
        draw_new.rectangle(
            [0, text_y, img_width, new_height],
            fill=(240, 240, 240),  # Light gray background
            outline='black',
            width=1
        )
        
        # Draw dialogue text (in order of speech)
        text_x = padding
        current_y = text_y + padding
        for line in wrapped_lines:
            # Check if line has character name (contains ":")
            if ":" in line:
                char_part, dialogue_part = line.split(":", 1)
                # Draw character name in bold
                draw_new.text((text_x, current_y), char_part + ":", fill='black', font=bold_font)
                # Measure character name width
                char_bbox = draw_new.textbbox((0, 0), char_part + ":", font=bold_font)
                char_width = char_bbox[2] - char_bbox[0]
                # Draw dialogue text
                draw_new.text((text_x + char_width + 5, current_y), dialogue_part, fill='black', font=font)
            else:
                # No character name, just dialogue
                draw_new.text((text_x, current_y), line, fill='black', font=font)
            current_y += line_height
        
        return new_img
    
    def _detect_faces(self, img: Image.Image):
        """Detect faces in image using OpenCV. Returns list of (x, y) face center positions."""
        if not FACE_DETECTION_AVAILABLE:
            return None
        
        try:
            import cv2
            
            # Convert PIL to numpy array (OpenCV uses BGR)
            img_array = np.array(img)
            if len(img_array.shape) == 3:
                # Convert RGB to BGR for OpenCV
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img_array
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if len(img_bgr.shape) == 3 else img_bgr
            
            # Load OpenCV's Haar Cascade face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            face_positions = []
            img_width, img_height = img.size
            
            for (x, y, w, h) in faces:
                # Calculate center of face
                center_x = int(x + w / 2)
                center_y = int(y + h / 2)
                face_positions.append((center_x, center_y))
            
            # Sort faces by x position (left to right) to match dialogue order
            face_positions.sort(key=lambda pos: pos[0])
            
            return face_positions if face_positions else None
                    
        except Exception as e:
            print(f"Face detection error: {e}, using fixed positions")
            return None
    
    def _calculate_bubble_positions_from_faces(self, face_positions: list, dialogues: list, img_size: tuple):
        """Calculate speech bubble positions based on detected face positions"""
        positions = []
        img_width, img_height = img_size
        
        # Match dialogues to faces (left to right)
        # Faces are already sorted by x position
        for i, dialogue_item in enumerate(dialogues):
            if i < len(face_positions):
                face_x, face_y = face_positions[i]
                
                # Position bubble above face
                # Try to place bubble above the face, but adjust if needed
                bubble_x = face_x
                
                # Position bubble above face with good spacing
                # If face is in upper half, place bubble at top
                # If face is in lower half, place bubble above face
                if face_y < img_height / 2:
                    bubble_y = max(30, face_y - 80)  # Above face
                else:
                    bubble_y = max(30, face_y - 120)  # More space above
                
                # Keep bubble within image bounds
                bubble_x = max(150, min(bubble_x, img_width - 150))
                bubble_y = max(30, min(bubble_y, img_height - 200))
                
                # Store target position (where tail should point - top of face/head area)
                # Point tail to upper part of face for better visual connection
                tail_target_y = max(face_y - 30, face_y - 50)  # Point to upper face/head area
                
                positions.append({
                    "bubble_center": (bubble_x, bubble_y),
                    "tail_target": (face_x, tail_target_y),
                    "character": dialogue_item.get("character", "")
                })
            else:
                # Fallback for extra dialogues (more dialogues than faces detected)
                positions.append(self._get_fixed_position(i, len(dialogues), img_size))
        
        return positions
    
    def _calculate_fixed_bubble_positions(self, dialogues: list, img_size: tuple):
        """Calculate fixed bubble positions when face detection fails"""
        positions = []
        img_width, img_height = img_size
        
        for i, dialogue_item in enumerate(dialogues):
            positions.append(self._get_fixed_position(i, len(dialogues), img_size))
        
        return positions
    
    def _get_fixed_position(self, index: int, total: int, img_size: tuple):
        """Get fixed position for bubble based on index"""
        img_width, img_height = img_size
        
        if total == 1:
            # Single dialogue: center-top
            bubble_x = img_width // 2
            bubble_y = 80
            tail_x = img_width // 2
            tail_y = 150
        elif total == 2:
            # Two dialogues: left and right
            if index == 0:
                bubble_x = img_width // 4
                bubble_y = 80
                tail_x = img_width // 4
                tail_y = 150
            else:
                bubble_x = 3 * img_width // 4
                bubble_y = 80
                tail_x = 3 * img_width // 4
                tail_y = 150
        else:
            # Multiple dialogues: distribute across top
            spacing = img_width // (total + 1)
            bubble_x = spacing * (index + 1)
            bubble_y = 80
            tail_x = spacing * (index + 1)
            tail_y = 150
        
        return {
            "bubble_center": (bubble_x, bubble_y),
            "tail_target": (tail_x, tail_y),
            "character": ""
        }
    
    def _draw_speech_bubble(self, draw: ImageDraw.Draw, dialogue_item: dict, position: dict, font, bold_font):
        """Draw a speech bubble with tail pointing to character"""
        char_name = dialogue_item.get("character", "")
        dialogue_text = dialogue_item.get("dialogue", "")
        bubble_center = position["bubble_center"]
        tail_target = position["tail_target"]
        
        # Get image size for bounds checking
        img = draw.im if hasattr(draw, 'im') else None
        if img:
            img_width, img_height = img.size
        else:
            # Get actual image dimensions (panels can be different sizes now)
            img_width, img_height = img.size
        
        # Calculate text dimensions
        if char_name:
            full_text = f"{char_name}: {dialogue_text}"
        else:
            full_text = dialogue_text
        
        # Wrap text to fit in bubble (max width ~300px)
        max_bubble_width = 300
        words = full_text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_bubble_width - 40:  # Padding
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate bubble size
        line_height = 22
        padding = 15
        if not lines:
            lines = [""]  # Handle empty dialogue
        bubble_width = max(150, min(max_bubble_width, max(draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0] for line in lines) + 40))
        bubble_height = len(lines) * line_height + padding * 2
        
        # Bubble position (center of bubble)
        bubble_x, bubble_y = bubble_center
        bubble_left = bubble_x - bubble_width // 2
        bubble_top = bubble_y - bubble_height // 2
        
        # Ensure bubble stays within image bounds (img_width/img_height already set above)
        bubble_left = max(10, min(bubble_left, img_width - bubble_width - 10))
        bubble_top = max(10, min(bubble_top, img_height - bubble_height - 50))
        
        # Draw bubble (rounded rectangle)
        bubble_right = bubble_left + bubble_width
        bubble_bottom = bubble_top + bubble_height
        corner_radius = 15
        
        # Draw clean rounded rectangle for bubble (simple white fill, black outline)
        # Use ImageDraw's rounded_rectangle if available (PIL 9.0+), otherwise draw manually
        try:
            # Try modern PIL rounded_rectangle method (cleanest)
            draw.rounded_rectangle(
                [bubble_left, bubble_top, bubble_right, bubble_bottom],
                radius=corner_radius,
                fill='white',
                outline='black',
                width=2
            )
        except (AttributeError, TypeError):
            # Fallback for older PIL: draw rounded rectangle manually
            # First, draw white fill (main rectangle)
            draw.rectangle(
                [bubble_left, bubble_top, bubble_right, bubble_bottom],
                fill='white'
            )
            # Draw rounded corner fills (white circles to create rounded effect)
            draw.ellipse(
                [bubble_left, bubble_top, bubble_left + corner_radius * 2, bubble_top + corner_radius * 2],
                fill='white'
            )
            draw.ellipse(
                [bubble_right - corner_radius * 2, bubble_top, bubble_right, bubble_top + corner_radius * 2],
                fill='white'
            )
            draw.ellipse(
                [bubble_left, bubble_bottom - corner_radius * 2, bubble_left + corner_radius * 2, bubble_bottom],
                fill='white'
            )
            draw.ellipse(
                [bubble_right - corner_radius * 2, bubble_bottom - corner_radius * 2, bubble_right, bubble_bottom],
                fill='white'
            )
            # Draw clean black outline (single rectangle, no overlapping)
            draw.rectangle(
                [bubble_left, bubble_top, bubble_right, bubble_bottom],
                fill=None,
                outline='black',
                width=2
            )
        
        # Draw tail pointing to character
        tail_x, tail_y = tail_target
        bubble_center_x = bubble_left + bubble_width // 2
        
        # Calculate where tail should connect to bubble (closest edge to character)
        # Determine which edge of bubble is closest to character
        dist_to_top = abs(tail_y - bubble_top)
        dist_to_bottom = abs(tail_y - bubble_bottom)
        dist_to_left = abs(tail_x - bubble_left)
        dist_to_right = abs(tail_x - bubble_right)
        
        # Find closest edge
        min_dist = min(dist_to_top, dist_to_bottom, dist_to_left, dist_to_right)
        
        if min_dist == dist_to_bottom:
            # Tail from bottom (character below bubble)
            tail_start_x = max(bubble_left + 20, min(tail_x, bubble_right - 20))
            tail_start_y = bubble_bottom
            tail_size = 15
        elif min_dist == dist_to_top:
            # Tail from top (character above bubble)
            tail_start_x = max(bubble_left + 20, min(tail_x, bubble_right - 20))
            tail_start_y = bubble_top
            tail_size = 15
        elif min_dist == dist_to_left:
            # Tail from left (character to left of bubble)
            tail_start_x = bubble_left
            tail_start_y = max(bubble_top + 20, min(tail_y, bubble_bottom - 20))
            tail_size = 15
        else:
            # Tail from right (character to right of bubble)
            tail_start_x = bubble_right
            tail_start_y = max(bubble_top + 20, min(tail_y, bubble_bottom - 20))
            tail_size = 15
        
        # Draw tail (triangle pointing to character)
        # Calculate direction vector from bubble to character
        dx = tail_x - tail_start_x
        dy = tail_y - tail_start_y
        # Normalize and create perpendicular for tail width
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx_norm = dx / length
            dy_norm = dy / length
            # Perpendicular vector for tail width
            perp_x = -dy_norm * tail_size
            perp_y = dx_norm * tail_size
        else:
            perp_x = tail_size
            perp_y = 0
        
        # Create tail triangle pointing to character (clean triangle)
        tail_points = [
            (tail_start_x, tail_start_y),  # Base point on bubble
            (tail_start_x + perp_x, tail_start_y + perp_y),  # One side
            (tail_x, tail_y),  # Point to character
            (tail_start_x - perp_x, tail_start_y - perp_y),  # Other side
        ]
        # Draw tail with white fill and black outline
        draw.polygon(tail_points, fill='white', outline='black', width=2)
        
        # Draw text in bubble
        text_y = bubble_top + padding
        for i, line in enumerate(lines):
            x_pos = bubble_left + padding
            if ":" in line and char_name:
                char_part, dialogue_part = line.split(":", 1)
                # Draw character name in bold
                draw.text((x_pos, text_y + i * line_height), char_part + ":", fill='black', font=bold_font)
                # Measure and draw dialogue
                char_bbox = draw.textbbox((0, 0), char_part + ":", font=bold_font)
                x_pos = bubble_left + padding + (char_bbox[2] - char_bbox[0]) + 5
                draw.text((x_pos, text_y + i * line_height), dialogue_part, fill='black', font=font)
            else:
                draw.text((x_pos, text_y + i * line_height), line, fill='black', font=font)
    
    def _add_narration_text(self, img: Image.Image, text: str):
        """Add narration text at bottom (for non-dialogue text)"""
        if not text:
            return img
        
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Get actual image dimensions (panels can be different sizes now)
        img_width, img_height = img.size
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        max_width = img_width - 40
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
        text_y = img_height - text_box_height - 10
        
        # Semi-transparent background
        overlay = Image.new('RGBA', (img_width, text_box_height), (255, 255, 255, 200))
        img_copy.paste(overlay, (0, text_y), overlay)
        
        # Draw text
        for i, line in enumerate(lines):
            draw.text((20, text_y + 10 + i * line_height), line, fill='black', font=font)
        
        return img_copy

