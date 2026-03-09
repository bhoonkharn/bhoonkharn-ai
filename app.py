import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)

# 2. ระบบสลับ API Key (Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()
genai.configure(api_key=random.choice(all_keys))

# 3. เตรียม AI Model
@st.cache_resource
def find_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower(): return m.name
        return "gemini-1.5-flash"
    except: return "gemini-1.5-flash"

model = genai.GenerativeModel(find_available_model())

# ระบบ Session สำหรับแชท
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# 4. เมนูเลือกรูปแบบข้อมูล
st.markdown("### 🛠️ เลือกรูปแบบข้อมูลที่คุณต้องการ")
analysis_mode = st.radio(
    "ระบบวิเคราะห์ข้อมูลตามความกังวลของคุณ:",
    ["📊 วิเคราะห์งานและผลกระทบต่อเนื่อง (Linked-Work Analysis)", 
     "💡 คู่มือตรวจรับงานฉบับเข้าใจง่าย (Simplified Checklist)"],
    index=0
)

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลนก่อสร้างอ้างอิง", type=['jpg', 'png', 'jpeg'], key="blue")
with col2:
    site_file = st.file_uploader("ภาพถ่ายหน้างานจริง", type=['jpg', 'png', 'jpeg'], key="site")

# 6. ปุ่มเริ่มวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์ข้อมูล", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังวิเคราะห์ผลกระทบลูกโซ่...'):
            try:
                # Prompt ใหม่: ปลดล็อกความรู้ AI + เน้น Domino Effect + ภาษาง่าย
                prompt = f"""
                คุณคือ 'BHOON KHARN AI Analysis' ที่ปรึกษาเทคนิคอัจฉริยะ (สุภาพ, มั่นคง, ไม่ใช้ ศิษย์/อาจารย์)
                หน้าที่ของคุณคือวิเคราะห์ภาพถ่ายงานก่อสร้าง โดยใช้โครงสร้างดังนี้:
                
                1. 🔍 วิเคราะห์สิ่งที่เห็น: สรุปงานในภาพ (สั้น/คม)
                2. ⚠️ ผลกระทบลูกโซ่ (Domino Effect): หากขั้นตอนนี้ผิดพลาด จะส่งผลเสียอย่างไรต่องานในอนาคต? 
                   (เช่น งานไฟพลาด -> งานฉาบเสีย -> งานสีร้าว -> ค่าซ่อมบานปลาย) เน้นให้เจ้าของบ้านเห็นความสำคัญ
                3. 🏠 มุมเจ้าของบ้าน (Checklist): วิธีตรวจง่ายๆ 1-2-3 (ใช้ภาษาง่ายที่สุด เปรียบเทียบกับของใกล้ตัว)
                4. 👷 ข้อมูลเชิงเทคนิค (Deep Dive): มาตรฐานวิศวกรรม/สถาปัตยกรรม (เช่น ระยะห่างบล็อก 3 ซม., การติดตาข่ายกันร้าว, การบ่มปูน)
                5. 💬 ประโยคคำถาม: ชุดคำถามสุภาพไว้คุยกับช่างหน้างาน
                
                กฎ: วิเคราะห์ตามรูปจริง, ไม่ฟันธงเด็ดขาดใช้คำว่า 'น่าสังเกตว่า', เน้นการป้องกันปัญหาก่อนงานถัดไปเริ่ม
                โหมดที่เลือกคือ: {analysis_mode}
                """
                
                images = []
                if blue_file: images.append(Image.open(blue_file))
                if site_file: images.append(Image.open(site_file))

                response = model.generate_content([prompt] + images)
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.analysis_done = True
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผลและแชท
if st.session_state.analysis_done:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์จาก BHOON KHARN AI")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt_chat := st.chat_input("สงสัยจุดไหน สอบถามที่ปรึกษา AI เพิ่มเติมได้เลยครับ..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})

        with st.chat_message("assistant"):
            chat_response = model.generate_content([f"คุณคือ BHOON KHARN AI Analysis วิเคราะห์ผลกระทบต่อเนื่องจากคำถามนี้: {prompt_chat}"])
            st.markdown(chat_response.text)
        st.session_state.messages.append({"role": "assistant", "content": chat_response.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์นี้เป็นเพียงการสังเกตการณ์เบื้องต้น โปรดปรึกษาวิศวกรของท่านเพื่อความถูกต้อง")
