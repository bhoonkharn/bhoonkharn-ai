import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")

st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>เปลี่ยนรูปถ่ายหน้างาน เป็นความรู้ที่ใช้งานได้จริง</p>", unsafe_allow_html=True)

# 2. ระบบสลับ API Key (Key Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ Secrets")
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

# 4. เมนูเลือกรูปแบบการวิเคราะห์ (ปรับเหลือ 2 หัวข้อตามที่พี่ต้องการ)
st.markdown("### 🛠️ คุณต้องการข้อมูลรูปแบบไหน?")
analysis_mode = st.radio(
    "เลือกตามความต้องการของคุณ:",
    ["⚡ วิเคราะห์เชิงลึกและงานที่เกี่ยวพัน (Technical & Linked Works)", 
     "🏠 คู่มือสำหรับเจ้าของบ้าน (Simple Self-Check Guide)"],
    index=0
)

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลนก่อสร้าง (เพื่อใช้อ้างอิง)", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, caption="แบบแปลนอ้างอิง", use_container_width=True)
with col2:
    site_file = st.file_uploader("รูปถ่ายหน้างานจริง", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, caption="หน้างานปัจจุบัน", use_container_width=True)

# 6. ประมวลผล
if st.button("🚀 เริ่มการวิเคราะห์ข้อมูล", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบ BHOON KHARN AI กำลังวิเคราะห์ข้อมูลและรวบรวมมาตรฐานอ้างอิง...'):
            try:
                # Prompt ใหม่ที่เน้น 2 หัวข้อหลัก
                common_instruction = """
                คุณคือที่ปรึกษาของ BHOON KHARN 
                - ห้ามฟันธงเด็ดขาด ใช้คำว่า 'น่าสังเกตว่า' หรือ 'ตรวจสอบเพิ่มเติมร่วมกับวิศวกร'
                - วิเคราะห์ตามรูปภาพจริงเท่านั้น
                """

                if "วิเคราะห์เชิงลึก" in analysis_mode:
                    mode_prompt = f"""{common_instruction}
                    รูปแบบการตอบ:
                    1. 🔍 รายละเอียดงานในภาพ: อธิบายว่างานที่เห็นคืออะไร มาตรฐานวิศวกรรม (วสท./มยผ.) ที่เกี่ยวข้องคืออะไร
                    2. 🔗 งานที่เกี่ยวพันกันต่อไป: งานนี้จะส่งผลต่อขั้นตอนถัดไปอย่างไร (เช่น งานระบบท่อ ส่งผลต่องานสถาปัตย์/ปูกระเบื้อง) และต้องดูอะไรเป็นพิเศษก่อนปิดงานส่วนนี้
                    3. 📚 ข้อมูลศึกษาเพิ่มเติม: แปะลิงก์ (ถ้ามี) หรือ Keywords สำหรับค้นหามาตรฐานอ้างอิง
                    """
                else:
                    mode_prompt = f"""{common_instruction}
                    รูปแบบการตอบ (เน้นเจ้าของบ้านที่ไม่รู้เรื่องช่าง):
                    1. ✅ วิธีตรวจง่ายๆ ด้วยตัวเอง: ใช้ตลับเมตร, ลูกดิ่ง, หรือสายตาอย่างไร ให้บอกเป็นข้อๆ 1-2-3
                    2. 💡 สิ่งที่ควรเอะใจ: จุดสังเกตที่ดูผิดปกติแบบภาษาบ้านๆ
                    3. 📖 เรื่องที่ควรศึกษาต่อ: แนะนำ 1-2 หัวข้อที่เจ้าของบ้านควรรู้สำหรับงานส่วนนี้
                    """

                content = [mode_prompt]
                if blue_file: content.append(Image.open(blue_file))
                if site_file: content.append(Image.open(site_file))

                response = model.generate_content(content)
                st.divider()
                st.markdown(response.text)
                
                st.success("🏗️ **BHOON KHARN: สร้างบ้านด้วยความเข้าใจ สบายใจทุกฝ่าย**")

            except google_exceptions.ResourceExhausted:
                st.warning("⚠️ โควตาชั่วคราวเต็ม ระบบกำลังสลับกุญแจสำรอง โปรดกดปุ่มอีกครั้งทันทีครับ")
            except Exception as e:
                st.error(f"ระบบขัดข้องชั่วคราว: {str(e)}")
            
            st.divider()
            st.caption("🚨 หมายเหตุ: AI เป็นเครื่องมือช่วยสังเกตการณ์เบื้องต้น โปรดใช้ข้อมูลนี้ปรึกษาหารือร่วมกับวิศวกรผู้ควบคุมงานเพื่อความถูกต้อง")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูปครับ")
