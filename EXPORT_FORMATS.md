# Export Formats - PDF and MP4

## Overview

The Comic Book Generator now supports **three export formats**:
1. **PNG** - Static image (original format)
2. **PDF** - Multi-page document (new)
3. **MP4** - Video with narration (new)

## PDF Export

### Features
- Multi-page PDF document
- Each panel on a separate page (or multiple panels per page if they fit)
- Panel numbers and narration text included
- Professional formatting with margins
- Easy to share and print

### Technical Details
- Uses ReportLab library
- Page size: US Letter (8.5" x 11")
- Panels are resized to fit page width with margins
- Text is wrapped and displayed below each panel

### Usage
- Automatically generated after comic creation
- Saved to: `output/comic.pdf`
- Downloadable from UI or CLI

## MP4 Video Export

### Features
- **Synchronized narration**: Each panel is shown with its corresponding narration audio
- **Sequential display**: Panels appear one at a time in order
- **Audio-driven timing**: Panel duration matches narration length
- **HD quality**: 1920x1080 resolution, 24fps
- **Professional format**: MP4 with H.264 video and AAC audio

### How It Works

1. **For each panel:**
   - Panel image is displayed
   - Corresponding narration audio plays
   - Panel stays visible for the duration of the audio
   - When audio ends, video transitions to next panel

2. **If no narration:**
   - Panel is shown for minimum 3 seconds
   - Video continues to next panel

3. **Video structure:**
   ```
   Panel 1 → [Narration 1 audio] → Panel 2 → [Narration 2 audio] → ... → Panel N
   ```

### Technical Details
- Uses MoviePy library
- Video resolution: 1920x1080 (HD)
- Frame rate: 24 fps
- Codec: H.264 (video), AAC (audio)
- Images are centered with black bars if aspect ratio doesn't match

### Usage
- Automatically generated after comic creation
- Saved to: `output/comic.mp4`
- Downloadable from UI or CLI
- Can be previewed in Streamlit UI

## File Locations

All export files are saved in the `output/` directory:

```
output/
├── comic.png          # PNG format (original)
├── comic.pdf          # PDF format (new)
├── comic.mp4          # MP4 video format (new)
├── narration/
│   ├── panel_1_narration.mp3
│   ├── panel_2_narration.mp3
│   └── ...
└── characters/
    ├── hero_reference.png
    └── ...
```

## Download Options

### In Streamlit UI:
- **Download Comic (PNG)** - Static image
- **Download Comic (PDF)** - PDF document
- **Download Video (MP4)** - Video with narration
- Individual narration files (MP3)

### In CLI:
All formats are automatically generated and saved to `output/` directory.

## Video Preview

In the Streamlit UI, you can:
- Preview the video directly in the browser
- Download the MP4 file
- Share the video file

## Requirements

### New Dependencies:
- **moviepy** - Video generation and editing
- **reportlab** - PDF generation
- **imageio-ffmpeg** - Video codec support (installed with moviepy)

### Installation:
```bash
pip install moviepy reportlab
```

These are already added to `requirements.txt`.

## Performance

### Generation Time:
- **PNG**: ~1 second (instant)
- **PDF**: ~2-3 seconds
- **MP4**: ~5-10 seconds (depends on video length)

### File Sizes (approximate):
- **PNG**: 1-2 MB (4 panels)
- **PDF**: 500 KB - 1 MB (4 panels)
- **MP4**: 2-5 MB (4 panels with narration)

## Use Cases

### PNG Format:
- Quick preview
- Social media sharing
- Web embedding

### PDF Format:
- Printing
- Document sharing
- Archiving
- Professional presentation

### MP4 Format:
- Social media (Instagram, TikTok, YouTube)
- Presentations
- Storytelling with audio
- Accessibility (audio narration)
- Engaging visual content

## Troubleshooting

### Video not generating?
- Check that narration files exist
- Ensure moviepy is installed: `pip install moviepy`
- Check for ffmpeg (required by moviepy)

### PDF not generating?
- Ensure reportlab is installed: `pip install reportlab`
- Check file permissions in output directory

### Video quality issues?
- Video is HD (1920x1080) by default
- Can be adjusted in `VideoGenerator` class
- Lower resolution = smaller file size

## Future Enhancements

Potential improvements:
- Custom video resolutions
- Transition effects between panels
- Background music option
- Subtitle/caption support
- Multiple export quality options

