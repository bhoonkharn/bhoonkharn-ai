import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")

st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างด้วยความเข้าใจ เพื่อความสบายใจของเจ้าของบ้าน</p>", unsafe_allow_html=True)

# 2. ระบบสลับ API Key
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

# 4. เมนูเลือกรูปแบบการวิเคราะห์
st.markdown("### 🛠️ เลือกหัวข้อที่คุณต้องการรับข้อมูล")
analysis_mode = st.radio(
    "รูปแบบการให้ข้อมูลของ BHOON KHARN:",
    ["⚡ รายการข้อสังเกตและจุดควรตรวจสอบ (Observation Checklist)", 
     "🛠️ คู่มือแนะนำการตรวจสอบหน้างานด้วยตนเอง (How-to-Check)", 
     "📖 เกร็ดความรู้พื้นฐานสำหรับงานส่วนนี้ (General Knowledge)"],
    index=0
)

# 5. ส่วนอัพโหลดรูป
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
        with st.spinner('ระบบกำลังวิเคราะห์ภาพและรวบรวมข้อมูลอ้างอิง...'):
            try:
                # Prompt ใหม่: เน้นการวิเคราะห์ตามเนื้อหาภาพจริง (Dynamic Advice)
                common_instruction = """
                คุณคือระบบสนับสนุนข้อมูลของ BHOON KHARN 
                กฎสำคัญ:
                1. วิเคราะห์ก่อนว่าภาพคือส่วนไหนของบ้าน (เช่น หลังคา, งานโครงสร้าง, งานผนัง, งานพื้น) 
                2. ให้คำแนะนำเฉพาะเรื่องที่เกี่ยวข้องกับภาพนั้นๆ เท่านั้น (ห้ามพูดเรื่องปูนหากเป็นรูปหลังคา)
                3. ไม่ฟันธงเด็ดขาด: ใช้คำว่า 'น่าสังเกตว่า' หรือ 'ตรวจสอบเพิ่มเติมร่วมกับแบบ' 
                4. อ้างอิงแบบ: หากมีแบบแปลน ให้พยายามดูว่าระยะหรือวัสดุในรูปดูใกล้เคียงกับในแบบหรือไม่
                5. ระบบดาว: ใช้ $★$ (ข้อสังเกตทั่วไป) ถึง $★★★$ (แนะนำให้ปรึกษาผู้ออกแบบ/วิศวกร)
                """

                if "รายการข้อสังเกต" in analysis_mode:
                    mode_prompt = f"{common_instruction}\nเน้นสรุปประเด็นที่เห็นจากภาพเปรียบเทียบกับแบบ (ถ้ามี) แจ้งจุดที่เจ้าของบ้านควร 'เอะใจ' เพื่อไปสอบถามต่อ"
                elif "คู่มือแนะนำการตรวจสอบ" in analysis_mode:
                    mode_prompt = f"{common_instruction}\nเน้นสอนวิธีดูหน้างานจริง เช่น 'วิธีเช็คการซ้อนทับของแผ่นหลังคา' หรือ 'วิธีเช็คแนวดิ่งของเสา' ตามที่ปรากฏในรูป"
                else:
                    mode_prompt = f"{common_instruction}\nเน้นอธิบายมาตรฐานทั่วไปของงานในภาพ และแปะ Keywords หรือลิงก์ที่เกี่ยวข้องเพื่อให้ลูกค้าไปศึกษาต่อเองได้"

                content = [mode_prompt]
                if blue_file: content.append(Image.open(blue_file))
                if site_file: content.append(Image.open(site_file))

                response = model.generate_content(content)
                st.divider()
                st.markdown(response.text)
                
                st.info("💡 **BHOON KHARN Suggestion:** การพูดคุยกับทีมช่างด้วยความเข้าใจ จะช่วยให้การสร้างบ้านเป็นเรื่องที่สนุกและราบรื่นครับ")

            except google_exceptions.ResourceExhausted:
                st.warning("⚠️ โควตาชั่วคราวเต็ม โปรดกดปุ่มอีกครั้งเพื่อสลับกุญแจครับ")
            except Exception as e:
                st.error(f"ระบบขัดข้องชั่วคราว: {str(e)}")
            
            st.divider()
            st.caption("🚨 หมายเหตุ: AI เป็นเครื่องมือช่วยสังเกตการณ์เบื้องต้น ข้อมูลนี้ควรนำไปปรึกษาวิศวกรหรือผู้ออกแบบของท่านอีกครั้งเพื่อความถูกต้อง")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูปครับ")
