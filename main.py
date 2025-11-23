"""
Main workflow orchestrator for Comic Book Generator v1.
"""
import os
from dotenv import load_dotenv
from story_generator import StoryGenerator
from image_generator import ImageGenerator
from narration_generator import NarrationGenerator
from comic_assembler import ComicAssembler

load_dotenv()

def main():
    print("=" * 50)
    print("Comic Book Generator v1")
    print("=" * 50)
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY not found!")
        print("Please create a .env file with your API keys.")
        print("See README.md for instructions.")
        return
    
    if not os.getenv("REPLICATE_API_TOKEN"):
        print("\n❌ ERROR: REPLICATE_API_TOKEN not found!")
        print("Please create a .env file with your API keys.")
        print("See README.md for instructions.")
        return
    
    # Get user input
    user_prompt = input("\nEnter your story idea: ").strip()
    if not user_prompt:
        user_prompt = "A hero saves the day"
        print(f"Using default: {user_prompt}")
    
    num_panels = input("Number of panels (3-5, default 4): ").strip()
    num_panels = int(num_panels) if num_panels.isdigit() and 3 <= int(num_panels) <= 5 else 4
    
    print(f"\nGenerating {num_panels}-panel comic about: {user_prompt}")
    print("This may take a few minutes...\n")
    
    try:
        # Initialize modules
        story_gen = StoryGenerator()
        image_gen = ImageGenerator()
        narration_gen = NarrationGenerator()
        assembler = ComicAssembler()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return
    
        # Step 1: Generate story
        print("Step 1/4: Generating story...")
        panels_data = story_gen.generate_story(user_prompt, num_panels)
        print(f"✓ Generated {len(panels_data)} panels")
        
        # Step 2: Generate images
        print("\nStep 2/4: Generating images...")
        panel_images = []
        for i, panel in enumerate(panels_data):
            print(f"  Generating image for panel {i+1}...")
            scene_desc = panel.get("scene_description", "")
            img = image_gen.generate_panel_image(scene_desc, panel.get("panel_number", i+1))
            panel_images.append(img)
        print("✓ All images generated")
        
        # Step 3: Generate narration
        print("\nStep 3/4: Generating narration...")
        audio_files = narration_gen.generate_all_narrations(panels_data)
        print(f"✓ Generated {len(audio_files)} narration files")
        
        # Step 4: Assemble comic
        print("\nStep 4/4: Assembling comic...")
        output_path = assembler.assemble_comic(panel_images, panels_data)
        print(f"✓ Comic assembled")
        
        # Summary
        print("\n" + "=" * 50)
        print("Generation Complete!")
        print("=" * 50)
        print(f"Comic saved to: {output_path}")
        if audio_files:
            print(f"Narration files saved to: output/narration/")
            print(f"  - {len(audio_files)} audio files generated")
        print("\nEnjoy your comic!")
    
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        print("Please check your API keys and try again.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

