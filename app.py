import streamlit as st
import os
from gtts import gTTS
import moviepy.editor as mp
from PIL import Image

st.set_page_config(page_title="Pro AI Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 प्रो AI वीडियो क्रिएटर")
st.write("रील्स (9:16), लॉन्ग वीडियो (16:9), और कूल ट्रांजिशन के साथ 100% वर्किंग ऐप!")

# 1. वीडियो फॉर्मेट / साइज (Ratio) चुनना
video_format = st.selectbox(
    "1. वीडियो का साइज़ (Format) चुनें:",
    ["Reels / Shorts (9:16 - Vertical)", "YouTube / Long Video (16:9 - Horizontal)"]
)

# 2. टेक्स्ट/नरेशन इनपुट
script = st.text_area(
    label="2. अपनी कहानी या नरेशन (Script) लिखें (हर लाइन में अलग बात लिखें):",
    value="",
    height=150,
    placeholder="लाइन 1: एक सुंदर जंगल था...\nलाइन 2: वहाँ एक शेर रहता था..."
)

# 3. इमेजेस अपलोड
uploaded_files = st.file_uploader(
    "3. अपनी तस्वीरें (Images) अपलोड करें:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

# वीडियो बनाएँ बटन
if st.button("🚀 वीडियो बनाएँ", use_container_width=True):
    if not script.strip():
        st.error("⚠️ कृपया पहले अपनी स्क्रिप्ट लिखें!")
    elif not uploaded_files:
        st.error("⚠️ कृपया कम से कम 1 या अधिक तस्वीरें अपलोड करें!")
    else:
        with st.spinner("⏳ वीडियो प्रोसेस हो रहा है... कृपया 1-2 मिनट प्रतीक्षा करें..."):
            try:
                # स्क्रिप्ट को लाइनों में तोड़ना
                lines = [line.strip() for line in script.split('\n') if line.strip()]
                if not lines:
                    lines = [script]
                
                audio_clips = []
                image_clips = []
                
                # आयाम (Dimensions) तय करना
                if "9:16" in video_format:
                    target_size = (1080, 1920) # रील्स साइज
                else:
                    target_size = (1920, 1080) # लॉन्ग वीडियो साइज
                
                for idx, line in enumerate(lines):
                    # 1. एरर-फ्री ऑडियो बनाना
                    tts = gTTS(text=line, lang='hi', slow=False)
                    audio_path = f"temp_audio_{idx}.mp3"
                    tts.save(audio_path)
                    
                    a_clip = mp.AudioFileClip(audio_path)
                    audio_clips.append(a_clip)
                    
                    # 2. फोटो को रीसाइज करना
                    img_file = uploaded_files[idx % len(uploaded_files)]
                    img_path = f"temp_img_{idx}.jpg"
                    
                    img = Image.open(img_file).convert("RGB")
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    img.save(img_path)
                    
                    # 3. इमेज क्लिप और स्मूथ फेड ट्रांजिशन
                    i_clip = mp.ImageClip(img_path).set_duration(a_clip.duration)
                    i_clip = i_clip.fadein(0.4).fadeout(0.4)
                    image_clips.append(i_clip)
                
                # सब कुछ जोड़ना
                final_audio = mp.concatenate_audioclips(audio_clips)
                final_video = mp.concatenate_videoclips(image_clips, method="compose")
                final_video = final_video.set_audio(final_audio)
                
                output_video_path = "final_output.mp4"
                final_video.write_videofile(
                    output_video_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac"
                )
                
                # सफलता और वीडियो दिखाना
                st.success("🎉 आपका वीडियो सफलतापूर्वक बन गया है!")
                st.video(output_video_path)
                
                # डाउनलोड बटन
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 वीडियो डाउनलोड करें",
                        data=file,
                        file_name="ai_generated_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ वीडियो बनाने में समस्या आई: {e}")
