import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")

st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างด้วยมาตรฐานวิศวกรรมสากล</p>", unsafe_allow_html=True)

# 2. ระบบสลับ API Key (Key Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key")
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

# 4. เมนูเลือกรูปแบบการวิเคราะห์ (2 หัวข้อตามที่พี่ต้องการ)
st.markdown("### 🛠️ เลือกรูปแบบการนำเสนอข้อมูล")
analysis_mode = st.radio(
    "รูปแบบที่คุณต้องการ:",
    ["🔍 วิเคราะห์ทางเทคนิคและลำดับงาน (Technical Insight)", 
     "🏠 คู่มือตรวจรับงานฉบับเข้าใจง่าย (Quick Checklist)"],
    index=0
)

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบก่อสร้างอ้างอิง", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, use_container_width=True)
with col2:
    site_file = st.file_uploader("ภาพถ่ายหน้างานจริง", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, use_container_width=True)

# 6. ปุ่มเริ่มวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('ระบบกำลังรวบรวมข้อมูลมาตรฐานวิศวกรรม...'):
            try:
                # Prompt ใหม่: ปลดล็อกความรู้ AI และปรับจูนแนวทาง BHOON KHARN
                common_instruction = """
                คุณคือ 'BHOON KHARN AI Analysis' ระบบวิเคราะห์งานก่อสร้างอัจฉริยะ 
                
                หน้าที่ของคุณ:
                1. ใช้ความรู้วิศวกรรมโยธาและสถาปัตยกรรมของคุณทั้งหมดในการวิเคราะห์ภาพ (ห้ามจำกัดความรู้)
                2. หากเป็นงานไฟฟ้า: ให้ความสำคัญกับระยะห่างระหว่างบล็อกไฟ (ควรห่าง 3 ซม. เพื่อความสวยงามของหน้ากาก)
                3. หากเป็นงานก่อนฉาบ: เตือนเรื่องการติดตาข่ายกันร้าว (Fiber Mesh) ทุกครั้งเพื่อป้องกันรอยร้าว
                4. หากเป็นงานปูน: ย้ำเรื่องการบ่มตัว (Curing) 14-21 วัน และห้ามเติมน้ำในคอนกรีต
                5. ใช้ภาษาสุภาพ เป็นมืออาชีพ (ไม่ต้องใช้ ศิษย์/อาจารย์)
                
                โครงสร้างการตอบ:
                - วิเคราะห์สิ่งที่เห็น (What is it?)
                - ข้อสังเกตเชิงเทคนิค (Technical Observations) โดยอ้างอิงมาตรฐาน วสท./มยผ. หรือมาตรฐานสากล
                - งานที่ต้องดำเนินการต่อและสิ่งที่ต้องระวัง (Next Steps & Precautions)
                - แหล่งศึกษาเพิ่มเติม (ลิงก์ หรือ Keywords)
                """
                
                if "วิเคราะห์ทางเทคนิค" in analysis_mode:
                    mode_prompt = f"{common_instruction}\nเน้นการเชื่อมโยงงานปัจจุบันกับงานที่จะตามมาในอนาคตเพื่อให้เจ้าของบ้านเตรียมตัวถูก"
                else:
                    mode_prompt = f"{common_instruction}\nเน้นสรุปเป็นข้อๆ เข้าใจง่าย บอกวิธีตรวจสอบด้วยตัวเองแบบ 1-2-3"

                images = []
                if blue_file: images.append(Image.open(blue_file))
                if site_file: images.append(Image.open(site_file))

                response = model.generate_content([mode_prompt] + images)
                
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.analysis_done = True
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผลและระบบแชท
if st.session_state.analysis_done:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์จาก BHOON KHARN AI")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("มีข้อสงสัยเกี่ยวกับงานส่วนนี้ สอบถามเพิ่มเติมได้ครับ..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("กำลังประมวลผลคำตอบ..."):
                chat_response = model.generate_content([f"คุณคือ BHOON KHARN AI Analysis ตอบคำถามนี้โดยใช้ความรู้วิศวกรรมของคุณ: {prompt}"])
                st.markdown(chat_response.text)
        st.session_state.messages.append({"role": "assistant", "content": chat_response.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์นี้เป็นเพียงการสังเกตการณ์เบื้องต้น โปรดปรึกษาวิศวกรของท่านเพื่อความถูกต้องตามหลักวิศวกรรม")
