import streamlit as st
import os
import asyncio
import edge_tts
import moviepy.editor as mp

st.set_page_config(page_title="AI Video Creator Pro", page_icon="🎬", layout="centered")

st.title("🎬 प्रो AI वीडियो क्रिएटर")
st.write("अपनी तस्वीरें अपलोड करें, मेल/फीमेल आवाज़ चुनें, और वीडियो बनाएँ!")

# 1. वीडियो फॉर्मेट / साइज
video_format = st.selectbox(
    "1. वीडियो का साइज़ (Format) चुनें:",
    ["Reels / Shorts (9:16 - वर्टिकल)", "YouTube / Long Video (16:9 - हॉरिजॉन्टल)"]
)

# 2. आवाज़ चुनना
voice_option = st.selectbox(
    "2. नरेटर की आवाज़ (Voice) चुनें:",
    ["फीमेल आवाज़ (hi-IN-SwaraNeural)", "मेल आवाज़ (hi-IN-MadhurNeural)"]
)

voice_code = "hi-IN-SwaraNeural" if "Swara" in voice_option else "hi-IN-MadhurNeural"

# 3. स्क्रिप्ट इनपुट
script = st.text_area(
    label="3. अपनी कहानी या नरेशन (Script) लिखें:",
    value="",
    height=150,
    placeholder="लाइन 1: एक सुंदर जंगल था...\nलाइन 2: वहाँ एक शेर रहता था..."
)

# 4. फोटो अपलोड करना
uploaded_files = st.file_uploader(
    "4. अपनी तस्वीरें (Images) अपलोड करें:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"✅ कुल {len(uploaded_files)} तस्वीरें जुड़ चुकी हैं!")

async def generate_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

if st.button("🚀 प्रो वीडियो बनाएँ", use_container_width=True):
    if not script.strip():
        st.error("⚠️ कृपया पहले अपनी स्क्रिप्ट लिखें!")
    elif not uploaded_files:
        st.error("⚠️ कृपया कम से कम 1 या अधिक तस्वीरें अपलोड करें!")
    else:
        with st.spinner("⏳ वीडियो प्रोसेस हो रहा है... कृपया प्रतीक्षा करें..."):
            try:
                lines = [line.strip() for line in script.split('\n') if line.strip()]
                if not lines:
                    lines = [script]
                
                audio_clips = []
                image_clips = []
                
                target_size = (1080, 1920) if "9:16" in video_format else (1920, 1080)
                
                for idx, line in enumerate(lines):
                    audio_path = f"temp_audio_{idx}.mp3"
                    asyncio.run(generate_audio(line, voice_code, audio_path))
                    
                    a_clip = mp.AudioFileClip(audio_path)
                    audio_clips.append(a_clip)
                    
                    img_file = uploaded_files[idx % len(uploaded_files)]
                    img_path = f"temp_img_{idx}.jpg"
                    
                    with open(img_path, "wb") as f:
                        f.write(img_file.getbuffer())
                    
                    clip_duration = a_clip.duration
                    i_clip = mp.ImageClip(img_path).set_duration(clip_duration)
                    i_clip = i_clip.resize(target_size)
                    i_clip = i_clip.resize(lambda t: 1 + 0.03 * t) 
                    i_clip = i_clip.fadein(0.3).fadeout(0.3)
                    image_clips.append(i_clip)
                
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
                
                st.success("🎉 आपका वीडियो बनकर तैयार है!")
                st.video(output_video_path)
                
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 वीडियो डाउनलोड करें",
                        data=file,
                        file_name="pro_animated_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ वीडियो बनाने में समस्या आई: {e}")
