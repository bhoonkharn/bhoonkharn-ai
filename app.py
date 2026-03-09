import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บให้คลีน
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ระบบตรวจงานก่อสร้างอัจฉริยะ</p>", unsafe_allow_html=True)

# 2. ตรวจสอบ API Key ใน Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()

# 3. ระบบค้นหาโมเดลที่ใช้งานได้จริง
@st.cache_resource
def find_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower():
                    return m.name
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models[0] if models else None
    except:
        return None

selected_model_name = find_available_model()

if selected_model_name:
    model = genai.GenerativeModel(selected_model_name)
else:
    st.error("❌ ไม่สามารถโหลด AI Model ได้")
    st.stop()

# 4. ส่วนอัพโหลดรูป (เพิ่มบรรทัดแสดงผลรูปกลับเข้าไปแล้วครับ)
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. อัพโหลดแบบ")
    blue_file = st.file_uploader("เลือกไฟล์แบบแปลน", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file:
        # บรรทัดนี้แหละครับที่ทำให้รูปโชว์
        st.image(blue_file, caption="แบบก่อสร้างอ้างอิง", use_container_width=True)

with col2:
    st.subheader("2. อัพโหลดรูปหน้างาน")
    site_file = st.file_uploader("เลือกรูปถ่ายหน้างานจริง", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file:
        # บรรทัดนี้แหละครับที่ทำให้รูปโชว์
        st.image(site_file, caption="รูปถ่ายหน้างานจริง", use_container_width=True)

# 5. ปุ่มเริ่มตรวจงาน
if st.button("🚀 เริ่มการตรวจสอบ", use_container_width=True):
    if blue_file and site_file:
        with st.spinner('AI กำลังวิเคราะห์เปรียบเทียบ...'):
            try:
                img_blue = Image.open(blue_file)
                img_site = Image.open(site_file)
                
                prompt = """คุณคือวิศวกรผู้เชี่ยวชาญของ BHOON KHARN จงเปรียบเทียบ 'แบบแปลน' และ 'หน้างานจริง' 
                ระบุจุดที่ผิดพลาดอย่างละเอียดเป็นข้อๆ หากงานเรียบร้อยดีให้กล่าวชื่นชม"""
                
                response = model.generate_content([prompt, img_blue, img_site])
                
                st.divider()
                st.subheader("📋 ผลลัพธ์จาก AI")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์: {e}")
    else:
        st.warning("กรุณาอัพโหลดรูปให้ครบทั้ง 2 ช่องครับ")
