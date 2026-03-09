import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)

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

# --- ส่วนใหม่: ตัวเลือกรูปแบบการตรวจ ---
st.markdown("### 🛠️ เลือกรูปแบบการวิเคราะห์")
analysis_mode = st.radio(
    "คุณต้องการให้ AI ช่วยตรวจแบบไหน?",
    ["สรุปประเด็นสำคัญ (เน้นกระชับ)", 
     "คู่มือตรวจงานด้วยตัวเอง (เน้นวิธีเช็ค)", 
     "อธิบายสำหรับมือใหม่ (เน้นความเข้าใจ)"],
    index=1 # ตั้งค่าเริ่มต้นที่ คู่มือตรวจงาน
)

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
        with st.spinner('ระบบกำลังวิเคราะห์ตามรูปแบบที่คุณเลือก...'):
            try:
                # ปรับเงื่อนไข Prompt ตามโหมดที่เลือก
                if "สรุปประเด็นสำคัญ" in analysis_mode:
                    mode_instruction = "เน้นสรุปใจความสำคัญ สั้น กระชับ ตรงไปตรงมา ชี้เฉพาะจุดที่เป็นปัญหาหลักเท่านั้น"
                elif "คู่มือตรวจงานด้วยตัวเอง" in analysis_mode:
                    mode_instruction = """เน้นการสอนเจ้าของบ้านให้ตรวจสอบด้วยตัวเอง โดยบอกว่า 'ควรเช็คอะไร' และ 'เช็คอย่างไร' 
                    เช่น การใช้ตลับเมตรวัด, การใช้ลูกดิ่ง, หรือการสังเกตด้วยตาเปล่า และย้ำเรื่องการห้ามเติมน้ำในคอนกรีต หรือระยะเวลาบ่มปูนก่อนทาสี"""
                else:
                    mode_instruction = "อธิบายอย่างละเอียดโดยไม่ใช้ศัพท์ช่างที่ยากเกินไป เปรียบเทียบให้เห็นภาพชัดเจน และบอกขั้นตอนที่ช่างกำลังจะทำในลำดับถัดไปเพื่อให้เตรียมตัวถูก"

                common_prompt = f"""
                จากการวิเคราะห์ของ AI ของ BHOON KHARN:
                คุณคือที่ปรึกษาของเจ้าของบ้าน {mode_instruction}
                
                หากพบจุดวิกฤตที่ต้องจัดการก่อนงานขั้นถัดไป ให้ใช้เครื่องหมาย 🚨 หรือตัวหนาสีแดง
                ย้ำ: ไม่ต้องใช้โทนเสียงจับผิดช่าง แต่ให้เน้นการเตรียมความพร้อมร่วมกัน
                """
                
                content_to_send = [common_prompt]
                if blue_file: content_to_send.append(Image.open(blue_file))
                if site_file: content_to_send.append(Image.open(site_file))

                response = model.generate_content(content_to_send)
                
                st.divider()
                st.subheader(f"📋 ผลการวิเคราะห์แบบ: {analysis_mode}")
                st.markdown(response.text)
                
                st.error("""
                **🚨 คำเตือน:** ข้อมูลนี้เป็นเพียงข้อสังเกตเบื้องต้นจาก AI ของ BHOON KHARN เพื่อช่วยเจ้าของบ้านเตรียมงาน 
                โปรดตรวจสอบร่วมกับวิศวกรหรือผู้ควบคุมงานจริงทุกครั้งก่อนเริ่มงานขั้นถัดไป
                """)
                
            except Exception as e:
                st.error(f"การประมวลผลล้มเหลว: {e}")
    else:
        st.warning("กรุณาอัพโหลดรูปเพื่อให้ AI ช่วยตรวจสอบครับ")
