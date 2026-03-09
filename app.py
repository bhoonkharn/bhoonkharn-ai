import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)

# 2. ตรวจสอบ API Key
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()

# 3. ระบบค้นหาโมเดลอัตโนมัติ
@st.cache_resource
def find_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower(): return m.name
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models[0] if models else None
    except: return None

selected_model_name = find_available_model()
model = genai.GenerativeModel(selected_model_name) if selected_model_name else None

# 4. เมนูเลือกรูปแบบการวิเคราะห์
st.markdown("### 🛠️ เลือกรูปแบบการวิเคราะห์ที่ท่านต้องการ")
analysis_mode = st.radio(
    "ระบบของ BHOON KHARN พร้อมช่วยคุณในรูปแบบดังนี้:",
    ["⚡ สรุปประเด็นด่วน (Quick Scan)", 
     "🛠️ คู่มือตรวจงานเอง (Self-Check Guide)", 
     "📖 คัมภีร์สำหรับมือใหม่ (Beginner's Handbook)"],
    index=1
)

# 5. ส่วนอัพโหลดรูป
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. แบบแปลน (ถ้ามี)")
    blue_file = st.file_uploader("เลือกไฟล์แบบ", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, use_container_width=True)

with col2:
    st.subheader("2. รูปหน้างานจริง")
    site_file = st.file_uploader("เลือกรูปหน้างาน", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, use_container_width=True)

# 6. ปุ่มเริ่มงาน
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบ BHOON KHARN AI กำลังประมวลผล...'):
            try:
                # ปรับ Prompt ตามโหมด
