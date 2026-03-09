import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ผู้ช่วยสังเกตการณ์งานก่อสร้าง เพื่อเจ้าของบ้าน</p>", unsafe_allow_html=True)

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

# 5. ปุ่มเริ่มงาน
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบกำลังประมวลผล...'):
            try:
                content_to_send = []
                
                # ปรับ Prompt ใหม่ให้ซอฟต์ลงและเน้น "คำแนะนำ"
                common_instruction = """
                จากการวิเคราะห์ของ AI ของ BHOON KHARN:
                หน้าที่ของคุณคือ 'ผู้ช่วยสังเกตการณ์' ให้แก่เจ้าของบ้าน 
                ไม่ต้องจ้องจับผิดอย่างรุนแรง แต่ให้เน้นการ 'ชี้จุดที่ควรตรวจสอบ' และ 'วิธีตรวจสอบ' 
                โดยสรุปเป็นข้อๆ ดังนี้:
                1. สิ่งที่น่าสังเกตในภาพนี้ (ใช้ภาษาสุภาพ ไม่ตัดสินว่าผิดทันที)
                2. จุดที่เจ้าของบ้านควรสอบถามหรือเช็คกับช่างอีกครั้ง
                3. วิธีการตรวจสอบเบื้องด้วยตัวเอง (เช่น การใช้ตลับเมตร, การเอาน้ำราด, การมองด้วยสายตา)
                """
                
                if blue_file and site_file:
                    prompt = common_instruction + "\nช่วยเปรียบเทียบภาพหน้างานกับแบบแปลน และให้คำแนะนำในการตรวจรับงาน"
                    content_to_send = [prompt, Image.open(blue_file), Image.open(site_file)]
                
                elif site_file:
                    prompt = common_instruction + "\nวิเคราะห์จากภาพหน้างานจริง และแนะนำจุดที่เจ้าของบ้านควรให้ความสำคัญในขั้นตอนนี้"
                    content_to_send = [prompt, Image.open(site_file)]
                
                else:
                    prompt = common_instruction + "\nวิเคราะห์แบบแปลนและสรุปจุดสำคัญที่เจ้าของบ้านควรเดินไปดูเมื่อเข้าหน้างาน"
                    content_to_send = [prompt, Image.open(blue_file)]

                response = model.generate_content(content_to_send)
                
                st.divider()
                st.subheader("📋 ข้อแนะนำในการตรวจสอบ")
                st.markdown(response.text)
                
                # Disclaimer ด้านกฎหมาย
                st.warning("""
                **⚠️ หมายเหตุสำคัญ:** ข้อมูลนี้เป็นเพียงข้อสังเกตเบื้องต้นจากระบบ AI ของ BHOON KHARN 
                เพื่อช่วยให้เจ้าของบ้านเห็นจุดสำคัญได้ง่ายขึ้นเท่านั้น 
                **โปรดปรึกษาและตรวจสอบร่วมกับวิศวกรหรือผู้ควบคุมงานโดยตรงทุกครั้งก่อนสรุปผลงาน**
                """)
                
            except Exception as e:
                st.error(f"การประมวลผลล้มเหลว: {e}")
    else:
        st.warning("กรุณาอัพโหลดรูปเพื่อเริ่มการวิเคราะห์ครับ")
