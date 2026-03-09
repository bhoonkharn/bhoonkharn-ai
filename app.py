import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)

# 2. ระบบสลับ API Key (Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()
genai.configure(api_key=random.choice(all_keys))

# 3. ค้นหาโมเดล
@st.cache_resource
def find_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower(): return m.name
        return "gemini-1.5-flash"
    except: return "gemini-1.5-flash"

model = genai.GenerativeModel(find_available_model())

# 4. เมนูเลือกรูปแบบ
st.markdown("### 🛠️ เลือกรูปแบบการสรุปข้อมูล")
analysis_mode = st.radio(
    "ระบบ BHOON KHARN พร้อมให้บริการข้อมูลในรูปแบบ:",
    ["⚡ สรุปประเด็นสำคัญ (Quick Scan)", 
     "🛠️ แนวทางการตรวจสอบระดับมืออาชีพ (Professional Guide)", 
     "📖 คลินิกบ้านสำหรับมือใหม่ (Educational Base)"],
    index=1
)

# 5. ส่วนอัพโหลด
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน (ถ้ามี)", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, use_container_width=True)
with col2:
    site_file = st.file_uploader("รูปหน้างานจริง", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, use_container_width=True)

# 6. ประมวลผล
if st.button("🚀 วิเคราะห์ข้อมูลเชิงลึก", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบกำลังประมวลผลข้อมูลอ้างอิงมาตรฐานวิศวกรรม...'):
            try:
                # Prompt กลางที่รวมกฎเหล็กที่พี่ต้องการ
                common_rules = """
                คุณคือระบบวิเคราะห์ AI ของ BHOON KHARN โดยมีเกณฑ์การตอบดังนี้:
                1. อ้างอิงมาตรฐานเสมอ: ระบุมาตรฐานวิศวกรรมเบื้องต้น (เช่น วสท. หรือ มยผ.) เพื่อให้ทราบเกณฑ์ที่ถูกต้อง
                2. การตรวจสอบด้วยตัวเอง (Self-Check): แนะนำให้เจ้าของบ้านเช็ค ขนาด (Dimension), ระยะห่าง (Spacing), แนวดิ่ง (Plumb), และได้ฉาก (Square) หรือไม่
                3. การปรึกษาผู้เชี่ยวชาญ: หากพบจุดที่มีความสำคัญระดับ 4-5 ดาว หรือเกี่ยวข้องกับโครงสร้างหลัก ให้ระบุชัดเจนว่า 'ต้องปรึกษาวิศวกรวิชาชีพทันที'
                4. ความรู้เชิงเทคนิค: ย้ำเรื่องห้ามเติมน้ำในคอนกรีต, การบ่มปูน, และระยะเวลาทิ้งแห้งก่อนทาสี (14-21 วัน)
                """

                if "สรุปประเด็นสำคัญ" in analysis_mode:
                    mode_prompt = f"{common_rules}\nโทน: สรุปสั้น กระชับ ใช้ระบบดาว $★$ ถึง $★★★★★$ บอกระดับความสำคัญ"
                elif "แนวทางการตรวจสอบระดับมืออาชีพ" in analysis_mode:
                    mode_prompt = f"{common_rules}\nโทน: ที่ปรึกษาเชิงเทคนิค เน้นขั้นตอนการตรวจเช็คด้วยตัวเอง 1-2-3"
                else: # คลินิกบ้านสำหรับมือใหม่
                    mode_prompt = f"{common_rules}\nโทน: ให้ความรู้พื้นฐาน อธิบายเหตุและผลตามหลักมาตรฐานช่าง"

                content = [mode_prompt]
                if blue_file: content.append(Image.open(blue_file))
                if site_file: content.append(Image.open(site_file))

                response = model.generate_content(content)
                st.divider
