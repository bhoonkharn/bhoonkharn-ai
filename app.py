import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ (Page Config ต้องอยู่บรรทัดแรกของโค้ด)
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")

# ส่วนหัวและโลโก้บริษัท
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ที่ปรึกษาการตรวจงานก่อสร้างอัจฉริยะ เพื่อบ้านที่ได้มาตรฐาน</p>", unsafe_allow_html=True)

# 2. ระบบสลับ API Key (Rotation) เพื่อเพิ่มโควตาฟรี
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ Secrets (โปรดเช็คการตั้งค่าใน Streamlit Cloud)")
    st.stop()

# สุ่มกุญแจทุกครั้งที่หน้าเว็บทำงาน
genai.configure(api_key=random.choice(all_keys))

# 3. ค้นหาโมเดลที่รองรับ (Auto-Select)
@st.cache_resource
def find_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower(): return m.name
        return "gemini-1.5-flash"
    except:
        return "gemini-1.5-flash"

selected_model_name = find_available_model()
model = genai.GenerativeModel(selected_model_name)

# 4. เมนูเลือกรูปแบบการวิเคราะห์ (UX)
with st.expander("💡 ทำไมต้องตรวจงานกับ BHOON KHARN AI?", expanded=False):
    st.markdown("""
    * **ป้องกันงานแก้:** ตรวจเช็คความถูกต้องเบื้องต้นก่อนเริ่มงานขั้นถัดไป
    * **เสริมความรู้:** รู้วิธีตรวจสอบดิ่ง-ฉาก-ระยะ ด้วยตัวเองง่ายๆ
    * **มาตรฐานวิศวกรรม:** อ้างอิงเกณฑ์ วสท. เพื่อความปลอดภัย
    """)

st.markdown("### 🛠️ เลือกรูปแบบการสรุปข้อมูล")
analysis_mode = st.radio(
    "ระบบ BHOON KHARN พร้อมให้บริการข้อมูลในรูปแบบ:",
    ["⚡ สรุปประเด็นสำคัญ (Quick Scan)", 
     "🛠️ แนวทางการตรวจสอบระดับมืออาชีพ (Professional Guide)", 
     "📖 คลินิกบ้านสำหรับมือใหม่ (Educational Base)"],
    index=1
)

# 5. ส่วนอัพโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน (ถ้ามี)", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file:
        st.image(blue_file, caption="แบบแปลนอ้างอิง", use_container_width=True)

with col2:
    site_file = st.file_uploader("รูปหน้างานจริง", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file:
        st.image(site_file, caption="หน้างานปัจจุบัน", use_container_width=True)

# 6. ส่วนประมวลผล (Core Logic)
if st.button("🚀 วิเคราะห์ข้อมูลเชิงลึก", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบกำลังประมวลผลข้อมูลอ้างอิงมาตรฐานวิศวกรรม...'):
            try:
                # Prompt ที่รวมกฎเหล็กของพี่ Nhum (ห้ามเติมน้ำ, บ่มปูน, เช็คดิ่ง-ฉาก)
                common_rules = """
                คุณคือระบบวิเคราะห์ AI ของ BHOON KHARN โดยมีเกณฑ์การตอบดังนี้:
                1. อ้างอิงมาตรฐานเสมอ: ระบุมาตรฐานวิศวกรรมเบื้องต้น (เช่น วสท. หรือ มยผ.)
                2. การตรวจสอบด้วยตัวเอง (Self-Check): แนะนำวิธีเช็ค ขนาด, ระยะห่าง, แนวดิ่ง (Plumb), และได้ฉาก (Square) โดยใช้อุปกรณ์ใกล้ตัว
                3. ระดับความสำคัญ (Star System): ใช้ระบบดาว $★$ ถึง $★★★★★$ บอกระดับความสำคัญของสิ่งที่ตรวจพบ
                4. การส่งต่อผู้เชี่ยวชาญ: หากพบจุดวิกฤต (4-5 ดาว) ให้แจ้งว่า 'ต้องปรึกษาวิศวกรวิชาชีพทันที'
                5. วิชาช่างสำคัญ: ย้ำเรื่องห้ามเติมน้ำในปูน, การบ่มปูน, และระยะทิ้งแห้งก่อนทาสี (14-21 วัน)
                """

                if "สรุปประเด็นสำคัญ" in analysis_mode:
                    mode_prompt = f"{common_rules}\nโทน: รายงานข้อเท็จจริง สรุปสั้น กระชับ ตรงประเด็นจุดเสี่ยง"
                elif "แนวทางการตรวจสอบระดับมืออาชีพ" in analysis_mode:
                    mode_prompt = f"{common_rules}\nโทน: ที่ปรึกษาเชิงเทคนิค สุภาพ มั่นคง สอนขั้นตอนการตรวจเช็ค 1-2-3"
                else:
                    mode_prompt = f"{common_rules}\nโทน: ให้ความรู้พื้นฐาน อธิบายเหตุและผลเพื่อให้เจ้าของบ้านเข้าใจง่ายที่สุด"

                # รวมข้อมูลส่งให้ AI
                content_payload = [mode_prompt]
                if blue_file:
                    content_payload.append(Image.open(blue_file))
                if site_file:
                    content_payload.append(Image.open(site_file))

                # เรียกใช้งาน AI
                response = model.generate_content(content_payload)
                
                # แสดงผลลัพธ์
                st.divider()
                st.markdown(response.text)
                st.success("🏗️ **BHOON KHARN มุ่งมั่นให้ทุกบ้านได้มาตรฐาน**")

            except google_exceptions.ResourceExhausted:
                st.warning("⚠️ โควตาชั่วคราวเต็ม ระบบกำลังสลับกุญแจสำรอง โปรดกด 'วิเคราะห์ข้อมูลเชิงลึก' อีกครั้งทันทีครับ")
            except Exception as e:
                st.error(f"ระบบขัดข้องชั่วคราว: {str(e)}")
            
            st.divider()
            st.caption("🚨 หมายเหตุ: ข้อมูลนี้เป็นข้อสังเกตเบื้องต้นเพื่อประกอบการตัดสินใจ โปรดตรวจสอบร่วมกับวิศวกรวิชาชีพทุกครั้ง")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูปก่อนเริ่มการวิเคราะห์ครับ")
