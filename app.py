import streamlit as st
import os
from gtts import gTTS
import moviepy.editor as mp
from PIL import Image

st.set_page_config(page_title="Pro AI Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 प्रो AI वीडियो क्रिएटर")
st.write("एक बार में ढेरों फोटो सेलेक्ट करें, रील्स/लॉन्ग वीडियो साइज़ चुनें, और वीडियो बनाएँ!")

# 1. वीडियो फॉर्मेट / साइज (Ratio) चुनना
video_format = st.selectbox(
    "1. वीडियो का साइज़ (Format) चुनें:",
    ["Reels / Shorts (9:16 - वर्टिकल)", "YouTube / Long Video (16:9 - हॉरिजॉन्टल)"]
)

# 2. आवाज़ का जेंडर (Voice Gender) चुनना
voice_gender = st.selectbox(
    "2. नरेटर की आवाज़ (Voice) चुनें:",
    ["फीमेल आवाज़ (Female)", "मेल आवाज़ (Male टोन)"]
)

# 3. टेक्स्ट/नरेशन इनपुट
script = st.text_area(
    label="3. अपनी कहानी या नरेशन (Script) लिखें (हर लाइन में अलग बात लिखें):",
    value="",
    height=150,
    placeholder="लाइन 1: एक सुंदर जंगल था...\nलाइन 2: वहाँ एक शेर रहता था..."
)

# 4. एक साथ कई तस्वीरें (Multiple Images) एक ही बार में अपलोड करने का बॉक्स
uploaded_files = st.file_uploader(
    "4. अपनी तस्वीरें (Images) यहाँ एक साथ सेलेक्ट करें:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True,
    help="यहाँ से आप एक बार में 10-12 या जितनी चाहें उतनी तस्वीरें एक साथ टिक करके अपलोड कर सकते हैं।"
)

# यदि तस्वीरें अपलोड हो गई हैं, तो उनकी संख्या और झलक दिखाएं
if uploaded_files:
    st.success(f"✅ कुल {len(uploaded_files)} तस्वीरें एक साथ सफलतापूर्वक आ गई हैं!")
    
    # अपलोड की गई फोटो को छोटी स्क्रीन पर लाइन से दिखाना ताकि पता चले कि सब आ गई हैं
    cols = st.beta_columns(min(len(uploaded_files), 4)) if hasattr(st, "beta_columns") else []
    
# वीडियो बनाएँ बटन
if st.button("🚀 प्रो वीडियो बनाएँ", use_container_width=True):
    if not script.strip():
        st.error("⚠️ कृपया पहले अपनी स्क्रिप्ट लिखें!")
    elif not uploaded_files:
        st.error("⚠️ कृपया कम से कम 1 या अधिक तस्वीरें अपलोड करें!")
    else:
        with st.spinner("⏳ सभी फोटो और ऑडियो को मिलाकर वीडियो प्रोसेस हो रहा है... कृपया प्रतीक्षा करें..."):
            try:
                # स्क्रिप्ट को लाइनों में तोड़ना
                lines = [line.strip() for line in script.split('\n') if line.strip()]
                if not lines:
                    lines = [script]
                
                audio_clips = []
                image_clips = []
                
                # मेल और फीमेल आवाज़ का टोन सेट करना
                tld_setting = 'com' if voice_gender == "फीमेल आवाज़ (Female)" else 'co.uk'
                
                # आयाम (Dimensions) तय करना
                if "9:16" in video_format:
                    target_size = (1080, 1920) # रील्स साइज
                else:
                    target_size = (1920, 1080) # लॉन्ग वीडियो साइज
                
                for idx, line in enumerate(lines):
                    # 1. ऑडियो बनाना
                    tts = gTTS(text=line, lang='hi', tld=tld_setting, slow=False)
                    audio_path = f"temp_audio_{idx}.mp3"
                    tts.save(audio_path)
                    
                    a_clip = mp.AudioFileClip(audio_path)
                    audio_clips.append(a_clip)
                    
                    # 2. एक साथ अपलोड की गई लिस्ट में से फोटो उठाना
                    img_file = uploaded_files[idx % len(uploaded_files)]
                    img_path = f"temp_img_{idx}.jpg"
                    
                    img = Image.open(img_file).convert("RGB")
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    img.save(img_path)
                    
                    # 3. इमेज क्लिप और स्मूथ फेड एनीमेशन
                    i_clip = mp.ImageClip(img_path).set_duration(a_clip.duration)
                    i_clip = i_clip.fadein(0.3).fadeout(0.3)
                    image_clips.append(i_clip)
                
                # सब कुछ जोड़ना
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
                
                # सफलता और वीडियो दिखाना
                st.success("🎉 आपका शानदार वीडियो बनकर तैयार है!")
                st.video(output_video_path)
                
                # डाउनलोड बटन
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 वीडियो डाउनलोड करें",
                        data=file,
                        file_name="my_pro_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ वीडियो बनाने में समस्या आई: {e}")
