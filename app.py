import streamlit as st
import google.generativeai as genai
from PIL import Image

# ตั้งค่าหน้าเว็บให้คลีนแบบ BHOON KHARN
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")

st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ระบบตรวจงานก่อสร้างอัจฉริยะ เปรียบเทียบแบบแปลนและหน้างานจริง</p>", unsafe_allow_html=True)

# ดึง API Key จากระบบความปลอดภัย
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("กรุณาตั้งค่า API Key ในระบบก่อนใช้งานครับ")

model = genai.GenerativeModel('models/gemini-1.5-flash')
# สร้าง 2 ช่องอัพโหลด
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. อัพโหลดแบบ")
    blueprint_file = st.file_uploader("เลือกไฟล์แบบแปลน", type=['pdf', 'jpg', 'png'], key="blue")
    if blueprint_file:
        st.image(blueprint_file, use_container_width=True)

with col2:
    st.subheader("2. อัพโหลดรูปหน้างาน")
    site_file = st.file_uploader("เลือกรูปถ่ายหน้างานจริง", type=['jpg', 'png'], key="site")
    if site_file:
        st.image(site_file, use_container_width=True)

# ปุ่มเริ่มตรวจงาน
if st.button("🚀 เริ่มการตรวจสอบ", use_container_width=True):
    if blueprint_file and site_file:
        with st.spinner('AI กำลังวิเคราะห์...'):
            img_blue = Image.open(blueprint_file)
            img_site = Image.open(site_file)
            
            prompt = """คุณคือวิศวกรตรวจสอบงานมืออาชีพของบริษัท BHOON KHARN 
            จงเปรียบเทียบภาพ 'แบบก่อสร้าง' และ 'ภาพหน้างานจริง' 
            บอกจุดที่ผิดพลาด หรือจุดที่ไม่ตรงตามแบบอย่างละเอียดเป็นข้อๆ 
            หากงานเรียบร้อยดี ให้กล่าวชมเชยและบอกว่าผ่านมาตรฐาน"""
            
            response = model.generate_content([prompt, img_blue, img_site])
            
            st.divider()
            st.subheader("📋 ผลลัพธ์จาก AI")
            st.write(response.text)
    else:
        st.warning("กรุณาอัพโหลดไฟล์ให้ครบทั้ง 2 ช่องก่อนกดปุ่มครับ")
