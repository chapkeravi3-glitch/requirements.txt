import streamlit as st
import os
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image

st.set_page_config(page_title="AI Video Creator", page_icon="🎬")

st.title("🎬 AI ऑटोमैटिक वीडियो क्रिएटर")
st.write("अपनी तस्वीरें अपलोड करें और नरेशन स्क्रिप्ट लिखें, ऐप अपने आप वीडियो बना देगा!")

# 1. टेक्स्ट/नरेशन इनपुट
script = st.text_area("1. यहाँ अपनी कहानी या नरेशन (Script) लिखें:", height=150, placeholder="उदाहरण: एक समय की बात है, एक सुंदर जंगल था...")

# 2. इमेजेस अपलोड
uploaded_files = st.file_uploader("2. अपनी तस्वीरें (Images) अपलोड करें:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("🚀 वीडियो बनाएँ"):
    if not script:
        st.error("कृपया पहले नरेशन/कहानी लिखें!")
    elif not uploaded_files:
        st.error("कृपया कम से कम एक फोटो अपलोड करें!")
    else:
        with st.spinner("ऑडियो और वीडियो प्रोसेस हो रहा है... कृपया थोड़ा इंतज़ार करें..."):
            try:
                # 1. वॉइस/ऑडियो बनाना (gTTS)
                tts = gTTS(text=script, lang='hi')
                audio_path = "narration.mp3"
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = audio_clip.duration # कुल ऑडियो समय
                
                # 2. इमेजेस का समय तय करना
                num_images = len(uploaded_files)
                duration_per_image = total_duration / num_images
                
                image_clips = []
                for idx, file in enumerate(uploaded_files):
                    img_path = f"temp_img_{idx}.png"
                    img = Image.open(file)
                    img.save(img_path)
                    
                    # इमेज क्लिप बनाना
                    clip = ImageClip(img_path).set_duration(duration_per_image)
                    image_clips.append(clip)
                
                # 3. सभी इमेजेस को जोड़कर वीडियो बनाना
                video_clip = concatenate_videoclips(image_clips, method="compose")
                video_clip = video_clip.set_audio(audio_clip)
                
                output_video_path = "final_output.mp4"
                video_clip.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
                
                # सफलता का संदेश और वीडियो दिखाना
                st.success("🎉 आपका वीडियो सफलतापूर्वक बन गया है!")
                st.video(output_video_path)
                
                # डाउनलोड बटन
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 वीडियो डाउनलोड करें",
                        data=file,
                        file_name="my_generated_video.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"वीडियो बनाने में कोई समस्या आई: {e}")
