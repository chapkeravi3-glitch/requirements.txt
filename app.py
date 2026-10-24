import streamlit as st
import os
from gtts import gTTS
import moviepy.editor as mp
from PIL import Image

st.set_page_config(page_title="Smart AI Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 स्मार्ट AI वीडियो क्रिएटर")
st.write("अब यह ऐप आपकी लिखी हर लाइन के हिसाब से सही फोटो को ऑटोमैटिक सेट करेगा!")

# 1. टेक्स्ट/नरेशन इनपुट (लाइन-बाय-लाइन)
script = st.text_area(
    label="1. अपनी कहानी या नरेशन (Script) लिखें (हर लाइन में अलग बात लिखें):",
    value="",
    height=180,
    placeholder="लाइन 1: एक सुंदर जंगल था...\nलाइन 2: वहाँ एक शेर रहता था...\nलाइन 3: सब जानवर खुश थे..."
)

# 2. इमेजेस अपलोड
uploaded_files = st.file_uploader(
    "2. अपनी तस्वीरें (Images) अपलोड करें (कितनी भी फोटो डालें):", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

# 3. आवाज़ की स्पीड चुनने का विकल्प
voice_speed = st.selectbox("3. आवाज़ की गति (Speed):", ["सामान्य (Normal)", "धीमी (Slow)"])
slow_setting = True if voice_speed == "धीमी (Slow)" else False

# 4. वीडियो बनाएँ बटन
if st.button("🚀 स्मार्ट वीडियो बनाएँ", use_container_width=True):
    if not script.strip():
        st.error("⚠️ कृपया पहले अपनी स्क्रिप्ट या कहानी लिखें!")
    elif not uploaded_files:
        st.error("⚠️ कृपया कम से कम 1 या अधिक तस्वीरें अपलोड करें!")
    else:
        with st.spinner("⏳ स्मार्ट तरीके से ऑडियो और वीडियो प्रोसेस हो रहा है... कृपया प्रतीक्षा करें..."):
            try:
                # स्क्रिप्ट को लाइनों में तोड़ना
                lines = [line.strip() for line in script.split('\n') if line.strip()]
                if not lines:
                    lines = [script]
                
                audio_clips = []
                image_clips = []
                
                # हर लाइन के लिए अलग ऑडियो और उसकी सही फोटो सेट करना
                for idx, line in enumerate(lines):
                    # 1. हर लाइन का अलग ऑडियो बनाना
                    tts = gTTS(text=line, lang='hi', slow=slow_setting)
                    audio_path = f"temp_audio_{idx}.mp3"
                    tts.save(audio_path)
                    
                    a_clip = mp.AudioFileClip(audio_path)
                    audio_clips.append(a_clip)
                    
                    # 2. उस लाइन के हिसाब से फोटो चुनना (अगर फोटो कम हैं तो रिपीट हो जाएंगी)
                    img_file = uploaded_files[idx % len(uploaded_files)]
                    img_path = f"temp_img_{idx}.jpg"
                    
                    img = Image.open(img_file).convert("RGB")
                    img.save(img_path)
                    
                    # 3. फोटो को ठीक उतने ही सेकंड का रखना जितने सेकंड की वो लाइन है
                    i_clip = mp.ImageClip(img_path).set_duration(a_clip.duration)
                    image_clips.append(i_clip)
                
                # सभी ऑडियो और वीडियो क्लिप्स को आपस में जोड़ना
                final_audio = mp.concatenate_audioclips(audio_clips)
                final_video = mp.concatenate_videoclips(image_clips, method="compose")
                final_video = final_video.set_audio(final_audio)
                
                output_video_path = "smart_final_output.mp4"
                final_video.write_videofile(
                    output_video_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac"
                )
                
                # सफलता का संदेश और वीडियो दिखाना
                st.success("🎉 आपका स्मार्ट वीडियो बनकर तैयार है!")
                st.video(output_video_path)
                
                # डाउनलोड बटन
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 वीडियो डाउनलोड करें",
                        data=file,
                        file_name="my_smart_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ वीडियो बनाने में समस्या आई: {e}")
