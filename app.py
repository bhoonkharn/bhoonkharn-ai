import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ระบบช่วยสังเกตการณ์งานก่อสร้างอัจฉริยะ</p>", unsafe_allow_html=True)

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

# 4. ส่วนอัพโหลดรูป
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. แบบแปลน (ถ้ามี)")
    blue_file = st.file_uploader("เลือกไฟล์แบบ", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, use_container_width=True)

with col2:
    st.subheader("2. รูปหน้างานจริง")
    site_file = st.file_uploader("เลือกรูปหน้างาน", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, use_container_width=True)

# 5. ปุ่มเริ่มตรวจงาน
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบกำลังประมวลผล...'):
            try:
                content_to_send = []
                
                # กรณีอัปโหลดทั้งคู่
                if blue_file and site_file:
                    prompt = "จากการวิเคราะห์ของ AI ของ BHOON KHARN: โปรดเปรียบเทียบภาพแบบแปลนและหน้างานจริง ระบุจุดที่น่าสังเกตว่าอาจไม่ตรงตามแบบหรืออาจมีความผิดพลาดเชิงช่าง"
                    content_to_send = [prompt, Image.open(blue_file), Image.open(site_file)]
                
                # กรณีมีเฉพาะรูปหน้างาน
                elif site_file:
                    prompt = "จากการวิเคราะห์ของ AI ของ BHOON KHARN: โปรดวิเคราะห์รูปถ่ายงานก่อสร้างนี้ ระบุจุดที่น่าสังเกตว่าอาจไม่เรียบร้อยหรืออาจผิดมาตรฐานงานช่างทั่วไป"
                    content_to_send = [prompt, Image.open(site_file)]
                
                # กรณีมีเฉพาะแบบแปลน
                else:
                    prompt = "จากการวิเคราะห์ของ AI ของ BHOON KHARN: โปรดสรุปรายละเอียดสำคัญจากแบบแปลนนี้ เพื่อใช้ในการเตรียมงานหรือตรวจสอบหน้างาน"
                    content_to_send = [prompt, Image.open(blue_file)]

                response = model.generate_content(content_to_send)
                
                st.divider()
                st.subheader("📋 ผลการวิเคราะห์")
                # แสดงผลการวิเคราะห์
                st.markdown(response.text)
                
                # ข้อความคำเตือนและ Disclaimer ด้านกฎหมาย
                st.warning("""
                **⚠️ หมายเหตุสำคัญ:** ข้อมูลข้างต้นเป็นเพียงข้อสังเกตเบื้องต้นจากการวิเคราะห์ของระบบ AI ของ BHOON KHARN เท่านั้น 
                ผลลัพธ์นี้อาจมีความคลาดเคลื่อนและไม่สามารถนำไปใช้อ้างอิงทางกฎหมายได้ 
                **เพื่อความถูกต้องและปลอดภัยสูงสุด โปรดตรวจสอบหน้างานร่วมกับวิศวกรควบคุมงานหรือผู้เชี่ยวชาญเฉพาะด้านอีกครั้งก่อนดำเนินการใดๆ**
                """)
                
            except Exception as e:
                st.error(f"การประมวลผลล้มเหลว: {e}")
    else:
        st.warning("กรุณาอัพโหลดรูปอย่างน้อย 1 รูปเพื่อเริ่มการวิเคราะห์ครับ")
