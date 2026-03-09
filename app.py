import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)

# 2. ตรวจสอบกุญแจ (API Key)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("❌ ไม่พบ API Key ใน Secrets")
    st.stop()

# 3. ระบบค้นหาโมเดลที่ใช้งานได้จริง (ป้องกัน 404)
@st.cache_resource
def find_available_model():
    try:
        # ดึงรายชื่อโมเดลทั้งหมดที่พี่มีสิทธิ์ใช้
        for m in genai.list_models():
            # ค้นหาโมเดลที่รองรับการวิเคราะห์ภาพ (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                # ลำดับความสำคัญ: เอา Flash ก่อน ถ้าไม่มีเอา Pro
                if 'flash' in m.name.lower():
                    return m.name
        # ถ้าหา Flash ไม่เจอเลย ให้เอาตัวแรกที่ใช้ได้
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models[0] if models else None
    except Exception as e:
        st.error(f"ไม่สามารถดึงรายชื่อโมเดลได้: {e}")
        return None

selected_model_name = find_available_model()

if selected_model_name:
    st.caption(f"🤖 ระบบกำลังใช้โมเดล: {selected_model_name}")
    model = genai.GenerativeModel(selected_model_name)
else:
    st.error("❌ บัญชี API ของคุณยังไม่รองรับโมเดลที่ต้องการ")
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
                
                prompt = "คุณคือวิศวกรอาวุโส เปรียบเทียบภาพแบบแปลนและหน้างานจริง ระบุจุดที่ผิดพลาดเป็นข้อๆ"
                
                response = model.generate_content([prompt, img_blue, img_site])
                
                st.success("✅ วิเคราะห์เสร็จสิ้น")
                st.divider()
                st.markdown(response.text)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")
    else:
        st.warning("กรุณาอัพโหลดรูปให้ครบทั้ง 2 ช่องครับ")
