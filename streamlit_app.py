"""
Streamlit UI for Comic Book Generator v1
"""
import streamlit as st
import os
from dotenv import load_dotenv
from story_generator import StoryGenerator
from image_generator import ImageGenerator
from narration_generator import NarrationGenerator
from comic_assembler import ComicAssembler
from character_generator import CharacterGenerator
from video_generator import VideoGenerator
from character_database import get_character_list, get_roles, PREDEFINED_CHARACTERS
from PIL import Image as PILImage

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Comic Book Generator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    """Check if API keys are configured"""
    openai_key = os.getenv("OPENAI_API_KEY")
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    
    if not openai_key or not replicate_token:
        return False, openai_key, replicate_token
    return True, openai_key, replicate_token

def initialize_modules():
    """Initialize all generator modules"""
    try:
        char_gen = CharacterGenerator()
        story_gen = StoryGenerator()
        image_gen = ImageGenerator()
        narration_gen = NarrationGenerator()
        assembler = ComicAssembler()
        video_gen = VideoGenerator()
        return char_gen, story_gen, image_gen, narration_gen, assembler, video_gen, None
    except ValueError as e:
        return None, None, None, None, None, None, str(e)

def main():
    # Header
    st.markdown('<p class="main-header">🎨 Comic Book Generator v1</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create AI-powered comic books with just a few clicks!</p>', unsafe_allow_html=True)
    
    # Check API keys
    keys_ok, openai_key, replicate_token = check_api_keys()
    
    if not keys_ok:
        st.error("⚠️ API Keys Not Configured")
        st.warning("Please set up your API keys in the `.env` file:")
        with st.expander("How to set up API keys"):
            st.markdown("""
            1. **Get OpenAI API Key:**
               - Go to https://platform.openai.com/api-keys
               - Create a new secret key
               
            2. **Get Replicate API Token:**
               - Go to https://replicate.com/account/api-tokens
               - Create a new token
               
            3. **Create `.env` file:**
               ```env
               OPENAI_API_KEY=sk-your-key-here
               REPLICATE_API_TOKEN=your-token-here
               ```
            """)
        st.stop()
    
    # Initialize session state for characters
    if 'characters' not in st.session_state:
        st.session_state.characters = []
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info("API keys are configured ✓")
        
        st.subheader("Character Selection")
        
        # Character type selector
        character_type = st.radio(
            "Existent or non-existent, imaginary characters?",
            ["Existent", "Non-existent"],
            help="Choose whether to use existing comic book characters or create custom ones"
        )
        
        # Character management section
        st.markdown("---")
        st.markdown("### Add Characters")
        
        if character_type == "Existent":
            # Existent character selection
            with st.form("add_existent_character", clear_on_submit=True):
                st.markdown("**Add Existing Character**")
                character_list = get_character_list()
                selected_char = st.selectbox("Character:", character_list, key="existent_char_select")
                roles = get_roles()
                selected_role = st.selectbox("Role:", roles, key="existent_role_select")
                
                if st.form_submit_button("➕ Add Character", use_container_width=True):
                    # Check if character already added
                    if any(c.get("name") == selected_char for c in st.session_state.characters):
                        st.warning(f"{selected_char} is already added!")
                    else:
                        st.session_state.characters.append({
                            "name": selected_char,
                            "role": selected_role,
                            "type": "existent",
                            "description": None,
                            "reference_image": None,
                            "reference_image_path": None
                        })
                        st.success(f"Added {selected_char} as {selected_role}")
                        st.rerun()
        else:
            # Non-existent character creation
            with st.form("add_custom_character", clear_on_submit=True):
                st.markdown("**Add Custom Character**")
                custom_name = st.text_input("Name:", key="custom_name_input", placeholder="Enter character name")
                roles = get_roles()
                custom_role = st.selectbox("Role:", roles, key="custom_role_select")
                custom_description = st.text_area(
                    "Description:",
                    key="custom_desc_input",
                    placeholder="Describe the character's appearance, powers, personality, etc.",
                    height=100
                )
                
                if st.form_submit_button("🎨 Generate Character", use_container_width=True):
                    if not custom_name or not custom_description:
                        st.warning("Please fill in name and description!")
                    else:
                        # Check if character already added
                        if any(c.get("name") == custom_name for c in st.session_state.characters):
                            st.warning(f"{custom_name} is already added!")
                        else:
                            # Add to session state (will be generated later)
                            st.session_state.characters.append({
                                "name": custom_name,
                                "role": custom_role,
                                "type": "non-existent",
                                "description": custom_description,
                                "reference_image": None,
                                "reference_image_path": None,
                                "needs_generation": True
                            })
                            st.success(f"Added {custom_name} as {custom_role}. Character will be generated when you create the comic.")
                            st.rerun()
        
        # Display selected characters
        st.markdown("---")
        st.markdown("### Selected Characters")
        if st.session_state.characters:
            for idx, char in enumerate(st.session_state.characters):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{char['name']}** ({char['role']})")
                        if char['type'] == 'non-existent':
                            st.caption(char.get('description', '')[:50] + "..." if len(char.get('description', '')) > 50 else char.get('description', ''))
                    with col2:
                        if st.button("🗑️", key=f"remove_{idx}", help="Remove character"):
                            st.session_state.characters.pop(idx)
                            st.rerun()
                    
                    # Regenerate button for non-existent characters
                    if char['type'] == 'non-existent' and char.get('reference_image'):
                        if st.button("🔄 Regenerate", key=f"regen_{idx}", use_container_width=True):
                            # Mark for regeneration
                            st.session_state.characters[idx]['needs_regeneration'] = True
                            st.info(f"Regenerating {char['name']}...")
                            st.rerun()
        else:
            st.info("No characters added yet. Add characters above.")
        
        st.markdown("---")
        st.subheader("Narration Voice")
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        selected_voice = st.selectbox("Select voice:", voice_options, index=0)
    
    # Main input form
    with st.form("comic_form"):
        st.header("📝 Create Your Comic")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_prompt = st.text_area(
                "Story Idea:",
                placeholder="e.g., A hero saves the city from a giant robot",
                height=100,
                help="Describe the story you want to create"
            )
        
        with col2:
            num_pages = st.number_input(
                "Number of Pages:",
                min_value=1,
                max_value=10,
                value=1,
                help="Total number of pages in the comic book"
            )
            
            avg_panels_per_page = st.number_input(
                "Average Panels per Page:",
                min_value=3.0,
                max_value=9.0,
                value=5.0,
                step=0.5,
                help="Average number of panels per page (actual may vary per page)"
            )
        
        # Calculate total panels (will be used to generate story)
        total_panels = int(num_pages * avg_panels_per_page)
        st.info(f"📊 Will generate approximately {total_panels} panels across {num_pages} page(s)")
        
        submitted = st.form_submit_button("🚀 Generate Comic", use_container_width=True)
    
    # Generate comic when form is submitted
    if submitted:
        if not user_prompt:
            st.warning("Please enter a story idea!")
            st.stop()
        
        if not st.session_state.characters:
            st.warning("Please add at least one character!")
            st.stop()
        
        # Initialize modules
        char_gen, story_gen, image_gen, narration_gen, assembler, video_gen, error = initialize_modules()
        if error:
            st.error(f"Configuration Error: {error}")
            st.stop()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 0: Generate characters (for consistency)
            status_text.text("👤 Step 0/6: Generating character descriptions and reference images...")
            progress_bar.progress(5)
            
            character_descriptions = {}
            character_names = []
            
            for char_data in st.session_state.characters:
                char_name = char_data['name']
                char_role = char_data['role']
                char_type = char_data['type']
                
                # Check if regeneration needed
                needs_regeneration = char_data.get('needs_regeneration', False)
                has_reference = char_data.get('reference_image') is not None
                
                if char_type == "existent":
                    # Generate from existing character database
                    if needs_regeneration or not has_reference:
                        status_text.text(f"👤 Generating {char_name}...")
                        generated_char = char_gen.generate_existent_character(
                            char_name, char_role, user_prompt, save_reference=True
                        )
                        character_descriptions[char_name] = generated_char
                    else:
                        # Use existing data
                        character_descriptions[char_name] = char_data
                else:
                    # Generate custom character
                    custom_desc = char_data.get('description', '')
                    if needs_regeneration or not has_reference:
                        status_text.text(f"👤 Generating custom character {char_name}...")
                        generated_char = char_gen.generate_custom_character(
                            char_name, char_role, custom_desc, user_prompt, save_reference=True
                        )
                        character_descriptions[char_name] = generated_char
                        # Update session state with generated data
                        char_data.update(generated_char)
                    else:
                        # Use existing data
                        character_descriptions[char_name] = char_data
                
                character_names.append(char_name)
            
            progress_bar.progress(15)
            status_text.text(f"✓ Generated {len(character_descriptions)} character descriptions")
            
            # Display character references
            with st.expander("👤 Character References", expanded=False):
                char_cols = st.columns(len(character_names))
                for idx, char_name in enumerate(character_names):
                    if char_name in character_descriptions:
                        with char_cols[idx] if idx < len(char_cols) else st.container():
                            char_data = character_descriptions[char_name]
                            st.markdown(f"**{char_name}** ({char_data.get('role', 'N/A')})")
                            if char_data.get('reference_image'):
                                st.image(char_data['reference_image'], width='stretch')
                            desc_obj = char_data.get('description', {})
                            if isinstance(desc_obj, dict):
                                desc = desc_obj.get('detailed_description', desc_obj.get('description', ''))
                            else:
                                desc = str(desc_obj)
                            st.caption(desc[:100] + "..." if len(desc) > 100 else desc)
            
            # Step 1: Generate story
            status_text.text("📖 Step 1/6: Generating story...")
            progress_bar.progress(20)
            
            # Use total panels calculated from pages and average
            panels_data = story_gen.generate_story(user_prompt, total_panels, character_names, character_descriptions)
            progress_bar.progress(25)
            status_text.text(f"✓ Generated {len(panels_data)} panels")
            
            # Display story preview
            with st.expander("📖 Story Preview", expanded=False):
                for panel in panels_data:
                    st.markdown(f"**Panel {panel.get('panel_number', '?')}:**")
                    st.write(f"Scene: {panel.get('scene_description', 'N/A')[:100]}...")
                    if panel.get('narration'):
                        st.write(f"Narration: {panel.get('narration')}")
                    st.divider()
            
            # Step 2: Generate images (with character consistency)
            status_text.text("🎨 Step 2/6: Generating images...")
            progress_bar.progress(30)
            
            # Generate a single seed for all panels to ensure consistency
            import random
            comic_seed = random.randint(0, 2**32 - 1)
            status_text.text(f"🎨 Using seed {comic_seed} for consistent character appearance...")
            
            # Set character descriptions and seed for consistency
            image_gen.set_character_descriptions(character_descriptions)
            image_gen.set_seed(comic_seed)
            
            panel_images = []
            
            # Create columns for image display
            cols = st.columns(total_panels)
            
            for i, panel in enumerate(panels_data):
                status_text.text(f"🎨 Generating image for panel {i+1}/{total_panels}... (This may take 10-30 seconds due to rate limiting)")
                progress_bar.progress(30 + int((i + 1) * 40 / total_panels))
                
                scene_desc = panel.get("scene_description", "")
                # Extract characters mentioned in scene
                chars_in_scene = [char for char in character_names if char.lower() in scene_desc.lower()]
                img = image_gen.generate_panel_image(scene_desc, panel.get("panel_number", i+1), characters_in_scene=chars_in_scene)
                panel_images.append(img)
                
                # Show progress after each image
                if img and not hasattr(img, '_is_placeholder'):
                    status_text.text(f"✓ Panel {i+1} generated successfully")
                
                # Display image in column
                with cols[i]:
                    st.image(img, caption=f"Panel {i+1}", width='stretch')
            
            progress_bar.progress(70)
            status_text.text("✓ All images generated")
            
            # Step 3: Generate narration
            status_text.text("🎤 Step 3/6: Generating narration...")
            progress_bar.progress(75)
            
            narration_gen.voice = selected_voice
            audio_files = narration_gen.generate_all_narrations(panels_data)
            progress_bar.progress(80)
            status_text.text(f"✓ Generated {len(audio_files)} narration files")
            
            # Step 4: Assemble comic (PNG)
            status_text.text("🖼️ Step 4/6: Assembling comic (PNG)...")
            progress_bar.progress(82)
            
            # Set page configuration
            assembler.set_page_config(num_pages, avg_panels_per_page)
            output_png_path = assembler.assemble_comic(panel_images, panels_data)
            progress_bar.progress(85)
            status_text.text("✓ Comic PNG assembled!")
            
            # Step 5: Generate PDF
            status_text.text("📄 Step 5/6: Generating PDF...")
            progress_bar.progress(87)
            pdf_path = assembler.assemble_comic_pdf(panel_images, panels_data)
            progress_bar.progress(92)
            
            # Step 6: Generate Video
            status_text.text("🎬 Step 6/6: Generating video with narration...")
            # Pass page configuration and assembler to video generator
            video_path = video_gen.generate_video(panel_images, audio_files, panels_data, num_pages=num_pages, avg_panels_per_page=avg_panels_per_page, assembler=assembler)
            progress_bar.progress(100)
            status_text.text("✓ All formats generated!")
            
            # Display final comic
            st.success("🎉 Comic Generation Complete!")
            st.header("📚 Your Comic")
            
            # Display final comic from file
            if os.path.exists(output_png_path):
                final_comic_img = PILImage.open(output_png_path)
                st.image(final_comic_img, width='stretch', caption="Your Generated Comic")
            else:
                st.warning("Comic file not found, but individual panels are shown above.")
            
            # Download section
            st.header("💾 Download")
            
            # Main download options
            download_cols = st.columns(3)
            
            with download_cols[0]:
                if os.path.exists(output_png_path):
                    with open(output_png_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Comic (PNG)",
                            data=file,
                            file_name="comic.png",
                            mime="image/png",
                            use_container_width=True
                        )
            
            with download_cols[1]:
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as file:
                        st.download_button(
                            label="📄 Download Comic (PDF)",
                            data=file,
                            file_name="comic.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            
            with download_cols[2]:
                if os.path.exists(video_path):
                    with open(video_path, "rb") as file:
                        st.download_button(
                            label="🎬 Download Video (MP4)",
                            data=file,
                            file_name="comic.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
            
            # Additional downloads
            with st.expander("🎤 Download Individual Narration Files"):
                if audio_files:
                    for audio_file in audio_files:
                        if os.path.exists(audio_file):
                            with open(audio_file, "rb") as file:
                                panel_num = os.path.basename(audio_file).replace("panel_", "").replace("_narration.mp4", "").replace("_narration.mp3", "")
                                st.download_button(
                                    label=f"🎤 Panel {panel_num} Narration",
                                    data=file,
                                    file_name=os.path.basename(audio_file),
                                    mime="audio/mpeg",
                                    key=f"audio_{panel_num}"
                                )
            
            # Play narration files and video
            if audio_files:
                st.header("🎵 Listen to Narration")
                for audio_file in audio_files:
                    if os.path.exists(audio_file):
                        panel_num = os.path.basename(audio_file).replace("panel_", "").replace("_narration.mp3", "")
                        st.audio(audio_file, format="audio/mpeg")
            
            # Show video preview
            if os.path.exists(video_path):
                st.header("🎬 Video Preview")
                st.video(video_path)
            
        except Exception as e:
            st.error(f"❌ Error during generation: {e}")
            st.exception(e)
            progress_bar.progress(0)
            status_text.text("")

if __name__ == "__main__":
    main()

