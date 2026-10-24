import streamlit as st
import os
from gtts import gTTS
import moviepy.editor as mp
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image

st.set_page_config(page_title="AI Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 AI ऑटोमैटिक वीडियो क्रिएटर")
st.write("अपनी तस्वीरें अपलोड करें और अपनी स्क्रिप्ट लिखें/पेस्ट करें!")

# 1. टेक्स्ट/नरेशन इनपुट (पेस्ट और मोबाइल फ्रेंडली)
script = st.text_area(
    label="1. यहाँ अपनी कहानी या नरेशन (Script) लिखें या पेस्ट करें:",
    value="",
    height=180,
    placeholder="यहाँ लॉन्ग-प्रेस करके अपनी कहानी पेस्ट (Paste) करें...",
    help="आप किसी भी मैसेज या नोट से यहाँ टेक्स्ट पेस्ट कर सकते हैं।"
)

# 2. इमेजेस अपलोड
uploaded_files = st.file_uploader(
    "2. अपनी तस्वीरें (Images) अपलोड करें:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

# 3. वीडियो बनाएँ बटन
if st.button("🚀 वीडियो बनाएँ", use_container_width=True):
    if not script.strip():
        st.error("⚠️ कृपया पहले कुछ टेक्स्ट या कहानी लिखें/पेस्ट करें!")
    elif not uploaded_files:
        st.error("⚠️ कृपया कम से कम 1 या 2 फोटो अपलोड करें!")
    else:
        with st.spinner("⏳ ऑडियो और वीडियो तैयार हो रहा है... कृपया 1-2 मिनट प्रतीक्षा करें..."):
            try:
                # 1. वॉइस/ऑडियो जनरेट करना (gTTS)
                tts = gTTS(text=script, lang='hi')
                audio_path = "narration.mp3"
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = audio_clip.duration # कुल समय
                
                # 2. इमेजेस का समय तय करना
                num_images = len(uploaded_files)
                duration_per_image = total_duration / num_images
                
                image_clips = []
                for idx, file in enumerate(uploaded_files):
                    img_path = f"temp_img_{idx}.jpg"
                    
                    # इमेज सेव करना
                    img = Image.open(file).convert("RGB")
                    img.save(img_path)
                    
                    # क्लिप बनाना
                    clip = ImageClip(img_path).set_duration(duration_per_image)
                    image_clips.append(clip)
                
                # 3. इमेजेस और ऑडियो को मर्ज करके वीडियो बनाना
                video_clip = concatenate_videoclips(image_clips, method="compose")
                video_clip = video_clip.set_audio(audio_clip)
                
                output_video_path = "final_output.mp4"
                video_clip.write_videofile(
                    output_video_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac"
                )
                
                # सफलता का संदेश और वीडियो दिखाना
                st.success("🎉 आपका वीडियो बनकर तैयार है!")
                st.video(output_video_path)
                
                # डाउनलोड बटन
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 वीडियो डाउनलोड करें",
                        data=file,
                        file_name="generated_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ वीडियो बनाने में कोई समस्या आई: {e}")
