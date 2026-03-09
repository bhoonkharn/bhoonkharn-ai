import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)

# 2. ระบบ API Key
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key")
    st.stop()
genai.configure(api_key=random.choice(all_keys))

# 3. เตรียม AI Model
model = genai.GenerativeModel("gemini-1.5-flash")

# --- ระบบ Session สำหรับเก็บประวัติ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_report" not in st.session_state:
    st.session_state.full_report = ""

# 4. เมนูเลือกรูปแบบ
analysis_mode = st.radio("เลือกรูปแบบข้อมูล:", ["🔬 วิเคราะห์เชิงลึก", "🏠 คู่มือเจ้าของบ้าน"])

# 5. ส่วนอัปโหลด
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน", type=['jpg', 'png', 'jpeg'])
with col2:
    site_file = st.file_uploader("ภาพหน้างาน", type=['jpg', 'png', 'jpeg'])

# 6. ประมวลผล
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('กำลังประมวลผล...'):
            prompt = f"คุณคือ BHOON KHARN AI Analysis วิเคราะห์งานก่อสร้างและผลกระทบต่อเนื่อง โหมด: {analysis_mode} เน้นกระชับ เทคนิคเชิงลึก และสรุปวิธีเช็คด่วน"
            
            imgs = []
            if blue_file: imgs.append(Image.open(blue_file))
            if site_file: imgs.append(Image.open(site_file))

            response = model.generate_content([prompt] + imgs)
            st.session_state.messages = [{"role": "assistant", "content": response.text}]
            st.session_state.full_report = response.text # เก็บไว้ทำไฟล์ดาวน์โหลด

# 7. แสดงผลและแชท
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 รายงานการวิเคราะห์")
    
    # --- ส่วนใหม่: ปุ่มดาวน์โหลดข้อมูล ---
    st.download_button(
        label="📥 ดาวน์โหลดสรุปรายงานนี้ (Text File)",
        data=st.session_state.full_report,
        file_name="BHOON_KHARN_Report.txt",
        mime="text/plain",
    )
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt_chat := st.chat_input("พิมพ์คำถามเพิ่มเติม..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})

        with st.chat_message("assistant"):
            resp = model.generate_content(f"คุณคือ BHOON KHARN AI Analysis ตอบคำถามเชิงลึก: {prompt_chat}")
            st.markdown(resp.text)
            st.session_state.full_report += f"\n\nคำถาม: {prompt_chat}\nคำตอบ: {resp.text}"
        st.session_state.messages.append({"role": "assistant", "content": resp.text})
