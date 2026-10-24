import streamlit as st
import os
import asyncio
import edge_tts
import moviepy.editor as mp
from PIL import Image

st.set_page_config(page_title="Pro AI Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 Pro AI Video Creator")
st.write("Apni photos ek sath upload karein, Male/Female aawaj sunein, aur animated video banayein!")

# 1. Video Format / Size (Ratio) chunna
video_format = st.selectbox(
    "1. Video ka Size (Format) chunein:",
    ["Reels / Shorts (9:16 - Vertical)", "YouTube / Long Video (16:9 - Horizontal)"]
)

# 2. Asli Male aur Female Aawaj chunna (100% Working)
voice_option = st.selectbox(
    "2. Narrator ki Aawaj (Voice) chunein:",
    ["Female Aawaj (Swara)", "Male Aawaj (Madhur)"]
)

# Voice Code set karna
voice_code = "hi-IN-SwaraNeural" if "Swara" in voice_option else "hi-IN-MadhurNeural"

# 3. Text / Narration Script Input
script = st.text_area(
    label="3. Apni kahani ya script likhein (Har line mein alag baat likhein):",
    value="",
    height=150,
    placeholder="Line 1: Ek sundar jungle tha...\nLine 2: Wahan ek sher rehta tha..."
)

# 4. Ek sath dher saari photos upload karne ka option
uploaded_files = st.file_uploader(
    "4. Apni ya apni pasand ki photos yahan ek sath select karein:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True,
    help="Phone gallery se ek sath multiple photos select karke upload karein."
)

if uploaded_files:
    st.success(f"✅ Kul {len(uploaded_files)} photos safalpurvak upload ho gayi hain!")

# Async Function - TTS aawaj generate karne ke liye
async def generate_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# Video Banayein Button
if st.button("🚀 Pro Video Banayein", use_container_width=True):
    if not script.strip():
        st.error("⚠️ Kripya pehle apni script likhein!")
    elif not uploaded_files:
        st.error("⚠️ Kripya kam se kam 1 ya adhik photos upload karein!")
    else:
        with st.spinner("⏳ Shandar animation aur HD audio ke sath video process ho raha hai... Kripya pratiksha karein..."):
            try:
                # Script ko lines mein todna
                lines = [line.strip() for line in script.split('\n') if line.strip()]
                if not lines:
                    lines = [script]
                
                audio_clips = []
                image_clips = []
                
                # Dimensions tay karna
                if "9:16" in video_format:
                    target_size = (1080, 1920) # Reels Size
                else:
                    target_size = (1920, 1080) # Long Video Size
                
                for idx, line in enumerate(lines):
                    # 1. Audio banana (Male ya Female voice ke sath)
                    audio_path = f"temp_audio_{idx}.mp3"
                    asyncio.run(generate_audio(line, voice_code, audio_path))
                    
                    a_clip = mp.AudioFileClip(audio_path)
                    audio_clips.append(a_clip)
                    
                    # 2. Upload ki gayi photos mein se photo chunna
                    img_file = uploaded_files[idx % len(uploaded_files)]
                    img_path = f"temp_img_{idx}.jpg"
                    
                    img = Image.open(img_file).convert("RGB")
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    img.save(img_path)
                    
                    # 3. Advanced Animation (Zoom-in effect + Fade Transition)
                    clip_duration = a_clip.duration
                    i_clip = mp.ImageClip(img_path).set_duration(clip_duration)
                    
                    # Smooth Zoom Effect
                    i_clip = i_clip.resize(lambda t: 1 + 0.04 * t) 
                    
                    # Fade-in aur Fade-out transition
                    i_clip = i_clip.fadein(0.4).fadeout(0.4)
                    image_clips.append(i_clip)
                
                # Sab kuch jodna
                final_audio = mp.concatenate_audioclips(audio_clips)
                final_video = mp.concatenate_videoclips(image_clips, method="compose")
                final_video = final_video.set_audio(final_audio)
                
                output_video_path = "pro_final_output.mp4"
                final_video.write_videofile(
                    output_video_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac"
                )
                
                # Safalta aur video dikhana
                st.success("🎉 Aapka shandar animated video ban kar taiyar hai!")
                st.video(output_video_path)
                
                # Download Button
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Video Download Karein",
                        data=file,
                        file_name="my_pro_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ Video banane mein samasya aayi: {e}")
