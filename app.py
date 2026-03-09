import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="centered")
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
st.markdown("### 🛠️ รูปแบบการนำเสนอข้อมูล")
analysis_mode = st.radio(
    "ระบบจะสรุปข้อมูลตามโหมดที่คุณเลือก:",
    ["🔬 วิเคราะห์เชิงลึกทางวิศวกรรม (Engineering Deep Dive)", 
     "🏠 คู่มือตรวจหน้างานฉบับย่อยง่าย (Executive Summary)"],
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
        with st.spinner('BHOON KHARN AI กำลังประมวลผลข้อมูลเชิงเทคนิค...'):
            try:
                # Prompt ใหม่: ปรับให้กระชับ เน้นเทคนิคเชิงลึก และสร้างคำถามต่อ
                prompt = f"""
                คุณคือ 'BHOON KHARN AI Analysis' ที่ปรึกษาเทคนิคอัจฉริยะ (สุภาพ, มืออาชีพ)
                
                หน้าที่ของคุณ:
                1. 🔍 วิเคราะห์สิ่งที่เห็น: บอกทันทีว่าคือส่วนไหนและทำอะไรอยู่ (เน้นความกระชับ)
                2. ⚠️ ผลกระทบลูกโซ่ (Domino Effect): ถ้าพลาดตรงนี้ งานส่วนไหนจะเสียหายตาม? เน้นความสำคัญเชิงโครงสร้างและค่าใช้จ่าย
                3. 🏗️ เทคนิคเชิงลึก (Technical Specs): ดึงข้อมูลทางวิศวกรรมสากล/วสท./มยผ. มาอธิบายเชิงลึก (เช่น ระยะห่าง, วัสดุ, มาตรฐานงานช่างที่ถูกต้อง)
                4. 🏠 สำหรับเจ้าของบ้าน: สรุปวิธีเช็คด่วน 1-2-3 (ใช้ภาษาเข้าใจง่าย เปรียบเทียบภาพชัดเจน)
                5. 💬 คำถามที่ท่านอาจสงสัย: แนะนำ 3 คำถามที่เจ้าของบ้านควรพิมพ์ถามต่อเกี่ยวกับงานในภาพนี้
                
                กฎ: สรุปเป็นหัวข้อ/Bullet point ให้อ่านง่ายที่สุด ห้ามเขียนเป็นก้อนยาว, ไม่ฟันธงเด็ดขาดใช้คำว่า 'น่าสังเกตว่า'
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

# 7. แสดงผลและระบบแชท
if st.session_state.analysis_done:
    st.divider()
    st.markdown("### 📋 รายงานการวิเคราะห์")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt_chat := st.chat_input("พิมพ์คำถามที่ท่านสงสัยต่อได้ที่นี่..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})

        with st.chat_message("assistant"):
            # การถามตอบในแชทจะเน้นการดึงข้อมูลเชิงลึกมาตอบโดยละเอียดตามคำขอ
            chat_context = f"คุณคือ BHOON KHARN AI Analysis วิเคราะห์ข้อมูลเชิงลึกและเทคนิคก่อสร้างจากคำถาม: {prompt_chat}"
            chat_response = model.generate_content(chat_context)
            st.markdown(chat_response.text)
        st.session_state.messages.append({"role": "assistant", "content": chat_response.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์นี้เป็นเพียงการสังเกตการณ์เบื้องต้น โปรดปรึกษาวิศวกรของท่านเพื่อความถูกต้องตามหลักวิศวกรรม")
