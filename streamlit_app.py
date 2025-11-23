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
        story_gen = StoryGenerator()
        image_gen = ImageGenerator()
        narration_gen = NarrationGenerator()
        assembler = ComicAssembler()
        return story_gen, image_gen, narration_gen, assembler, None
    except ValueError as e:
        return None, None, None, None, str(e)

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
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info("API keys are configured ✓")
        
        st.subheader("Character Selection")
        characters = st.multiselect(
            "Choose characters:",
            ["hero", "villain", "sidekick"],
            default=["hero", "villain"]
        )
        
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
            num_panels = st.slider(
                "Number of Panels:",
                min_value=3,
                max_value=5,
                value=4,
                help="Choose between 3-5 panels for your comic"
            )
        
        submitted = st.form_submit_button("🚀 Generate Comic", use_container_width=True)
    
    # Generate comic when form is submitted
    if submitted:
        if not user_prompt:
            st.warning("Please enter a story idea!")
            st.stop()
        
        # Initialize modules
        story_gen, image_gen, narration_gen, assembler, error = initialize_modules()
        if error:
            st.error(f"Configuration Error: {error}")
            st.stop()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Generate story
            status_text.text("📖 Step 1/4: Generating story...")
            progress_bar.progress(10)
            
            panels_data = story_gen.generate_story(user_prompt, num_panels, characters)
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
            
            # Step 2: Generate images
            status_text.text("🎨 Step 2/4: Generating images...")
            progress_bar.progress(30)
            
            panel_images = []
            image_placeholders = []
            
            # Create columns for image display
            cols = st.columns(num_panels)
            
            for i, panel in enumerate(panels_data):
                status_text.text(f"🎨 Generating image for panel {i+1}/{num_panels}...")
                progress_bar.progress(30 + int((i + 1) * 40 / num_panels))
                
                scene_desc = panel.get("scene_description", "")
                img = image_gen.generate_panel_image(scene_desc, panel.get("panel_number", i+1))
                panel_images.append(img)
                
                # Display image in column
                with cols[i]:
                    st.image(img, caption=f"Panel {i+1}", use_container_width=True)
            
            progress_bar.progress(70)
            status_text.text("✓ All images generated")
            
            # Step 3: Generate narration
            status_text.text("🎤 Step 3/4: Generating narration...")
            progress_bar.progress(75)
            
            narration_gen.voice = selected_voice
            audio_files = narration_gen.generate_all_narrations(panels_data)
            progress_bar.progress(90)
            status_text.text(f"✓ Generated {len(audio_files)} narration files")
            
            # Step 4: Assemble comic
            status_text.text("🖼️ Step 4/4: Assembling comic...")
            progress_bar.progress(95)
            
            output_path = assembler.assemble_comic(panel_images, panels_data)
            progress_bar.progress(100)
            status_text.text("✓ Comic assembled!")
            
            # Display final comic
            st.success("🎉 Comic Generation Complete!")
            st.header("📚 Your Comic")
            
            # Display final comic from file
            if os.path.exists(output_path):
                final_comic_img = PILImage.open(output_path)
                st.image(final_comic_img, use_container_width=True, caption="Your Generated Comic")
            else:
                st.warning("Comic file not found, but individual panels are shown above.")
            
            # Download section
            st.header("💾 Download")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if os.path.exists(output_path):
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Comic (PNG)",
                            data=file,
                            file_name="comic.png",
                            mime="image/png",
                            use_container_width=True
                        )
            
            with col2:
                if audio_files:
                    st.write("**Narration Files:**")
                    for audio_file in audio_files:
                        if os.path.exists(audio_file):
                            with open(audio_file, "rb") as file:
                                panel_num = os.path.basename(audio_file).replace("panel_", "").replace("_narration.mp3", "")
                                st.download_button(
                                    label=f"🎤 Download Panel {panel_num} Narration",
                                    data=file,
                                    file_name=os.path.basename(audio_file),
                                    mime="audio/mpeg",
                                    key=f"audio_{panel_num}"
                                )
            
            # Play narration files
            if audio_files:
                st.header("🎵 Listen to Narration")
                for audio_file in audio_files:
                    if os.path.exists(audio_file):
                        panel_num = os.path.basename(audio_file).replace("panel_", "").replace("_narration.mp3", "")
                        st.audio(audio_file, format="audio/mpeg")
            
        except Exception as e:
            st.error(f"❌ Error during generation: {e}")
            st.exception(e)
            progress_bar.progress(0)
            status_text.text("")

if __name__ == "__main__":
    main()

