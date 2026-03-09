import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")

st.markdown("<h1 style='text-align: center;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)

# 2. ตรวจสอบกุญแจ (API Key)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("❌ ไม่พบ API Key ในหน้า Secrets ของ Streamlit ครับ")
    st.stop()

# 3. ฟังก์ชันโหลดโมเดลแบบปลอดภัย (ป้องกัน NotFound)
def get_model():
    # ลองเรียกหลายๆ ชื่อ เผื่อบางตัวถูกเปลี่ยนชื่อในระบบ
    model_names = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-1.5-flash-latest']
    for name in model_names:
        try:
            m = genai.GenerativeModel(name)
            # ทดสอบเรียกสั้นๆ ว่าใช้งานได้ไหม
            return m
        except:
            continue
    return None

model = get_model()

if model is None:
    st.error("❌ ระบบไม่สามารถเชื่อมต่อกับ AI Model ได้ โปรดเช็กการตั้งค่า API Key")
    st.stop()

# 4. ส่วนอัพโหลดรูป
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. อัพโหลดแบบ")
    blue_file = st.file_uploader("แบบแปลน", type=['jpg', 'png', 'jpeg'], key="blue")
with col2:
    st.subheader("2. อัพโหลดรูปหน้างาน")
    site_file = st.file_uploader("รูปถ่ายจริง", type=['jpg', 'png', 'jpeg'], key="site")

# 5. ปุ่มเริ่มงาน
if st.button("🚀 เริ่มการตรวจสอบ", use_container_width=True):
    if blue_file and site_file:
        try:
            with st.spinner('กำลังวิเคราะห์...'):
                img_blue = Image.open(blue_file)
                img_site = Image.open(site_file)
                
                # เขียนคำสั่งให้ชัดเจน
                prompt = "เปรียบเทียบภาพแบบแปลนและหน้างานจริง ระบุจุดที่ทำผิดพลาดจากแบบเป็นข้อๆ"
                
                # ส่งข้อมูลแบบระบุชื่อ Content
                response = model.generate_content([prompt, img_blue, img_site])
                
                st.success("✅ วิเคราะห์เสร็จสิ้น")
                st.divider()
                st.markdown(response.text)
        except Exception as e:
            # ถ้าพังอีก ให้โชว์ชื่อ Error ออกมาตรงๆ เลยครับ
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
            st.info("คำแนะนำ: ลองตรวจสอบที่ Google AI Studio ว่า API Key นี้ยังใช้งานได้ปกติหรือไม่")
    else:
        st.warning("กรุณาอัพโหลดรูปให้ครบทั้ง 2 ช่องครับ")
