import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ (Page Config)
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์ผลกระทบงานก่อสร้างและมาตรฐานวิศวกรรมสากล</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบสลับ API Key (Key Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ Secrets")
    st.stop()

# 3. ระบบโหลดโมเดลแบบ Robust (แก้ปัญหา NotFound)
@st.cache_resource
def load_bhoonkharn_model(api_key):
    genai.configure(api_key=api_key)
    try:
        # พยายามหารุ่น Flash ที่ดีที่สุดในปัจจุบัน
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # ค้นหาคำว่า flash ในชื่อรุ่น
        flash_models = [m for m in available_models if 'flash' in m.lower()]
        
        if flash_models:
            # ใช้รุ่นล่าสุดที่เจอ (เช่น gemini-1.5-flash หรือ gemini-2.0-flash ในปี 2026)
            target_model = flash_models[0]
            return genai.GenerativeModel(target_model), target_model
        else:
            # ถ้าไม่เจอคำว่า flash ให้หยิบอันแรกที่ส่งงานได้มาเลย
            return genai.GenerativeModel(available_models[0]), available_models[0]
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลโมเดลได้: {e}")
        return None, None

# สุ่มกุญแจและโหลดโมเดล
selected_key = random.choice(all_keys)
model, active_model_name = load_bhoonkharn_model(selected_key)

if not model:
    st.stop()

# --- ระบบ Session สำหรับเก็บประวัติ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_report" not in st.session_state:
    st.session_state.full_report = ""

# 4. Sidebar การตั้งค่า
with st.sidebar:
    st.title("⚙️ BHOON KHARN Config")
    st.info(f"🟢 Active Model: {active_model_name}")
    analysis_mode = st.radio(
        "โหมดการนำเสนอ:",
        ["📊 วิเคราะห์เทคนิคเชิงลึก (Linked-Work Focus)", 
         "🏠 คู่มือสำหรับเจ้าของบ้าน (Easy-to-Understand)"]
    )
    if st.button("🗑️ ล้างประวัติทั้งหมด"):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.rerun()

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลนก่อสร้าง", type=['jpg', 'png', 'jpeg'])
    if blue_file: st.image(blue_file, caption="แบบอ้างอิง", use_container_width=True)
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_file: st.image(site_file, caption="หน้างานปัจจุบัน", use_container_width=True)

# 6. ประมวลผล (Core Logic)
if st.button("🚀 เริ่มการวิเคราะห์เชิงลึก", use_container_width=True):
    if site_file or blue_file:
        with st.spinner(f'BHOON KHARN AI ({active_model_name}) กำลังวิเคราะห์...'):
            try:
                # ปลดล็อกสมอง AI + Domino Effect + ภาษาเจ้าของบ้าน
                prompt = f"""
                คุณคือ 'BHOON KHARN AI Analysis' ผู้เชี่ยวชาญเทคนิคก่อสร้างอิสระ
                วิเคราะห์ภาพนี้โดยใช้ความรู้เชิงวิศวกรรมทั้งหมดที่คุณมี และจัดระเบียบเนื้อหาดังนี้:
                
                1. 🔍 สิ่งที่เห็น: งานส่วนนี้คืออะไร และปัจจุบันทำถึงขั้นตอนไหน (กระชับ/คม)
                2. ⚠️ ผลกระทบลูกโซ่ (Domino Effect): **สำคัญมาก** ถ้าจุดนี้ทำพลาด จะเกิดปัญหาอะไรตามมาในงานถัดไป? ส่งผลเสียต่องบประมาณหรือความปลอดภัยอย่างไร?
                3. 🏗️ เทคนิคเชิงลึก: ดึงมาตรฐาน (วสท./มยผ.) หรือหลักวิชาช่างที่ถูกต้องมาอธิบาย (เช่น ระยะห่าง, การติดตั้ง, วัสดุ) 
                4. 🏠 มุมเจ้าของบ้าน: วิธีตรวจสอบง่ายๆ 1-2-3 (ใช้ภาษาชาวบ้าน เปรียบเทียบภาพให้เห็นชัด)
                5. 💬 ถามที่ปรึกษาต่อ: แนะนำ 3 หัวข้อคำถามเชิงลึกที่เจ้าของบ้านควรรู้เพิ่มเกี่ยวกับงานนี้
                
                กฎ: 
                - สรุปเป็นหัวข้อ/Bullet points ให้อ่านง่ายที่สุด
                - ห้ามฟันธงเด็ดขาด ใช้คำว่า 'น่าสังเกตว่า' หรือ 'แนะนำให้ยืนยันกับวิศวกร'
                - โหมดปัจจุบัน: {analysis_mode}
                """
                
                imgs = []
                if blue_file: imgs.append(Image.open(blue_file))
                if site_file: imgs.append(Image.open(site_file))

                response = model.generate_content([prompt] + imgs)
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูปครับ")

# 7. แสดงรายงานและแชท
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 รายงานวิเคราะห์หน้างาน")
    
    # ปุ่มดาวน์โหลด
    st.download_button(
        label="📥 ดาวน์โหลดรายงานเก็บไว้ (Text)",
        data=st.session_state.full_report,
        file_name="BHOON_KHARN_Analysis.txt",
        mime="text/plain"
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ช่องแชทถามตอบ
    if prompt_chat := st.chat_input("มีข้อสงสัย? พิมพ์ถามที่ปรึกษา AI เพิ่มเติมได้ที่นี่..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})

        with st.chat_message("assistant"):
            with st.spinner("กำลังค้นคว้าข้อมูลเทคนิค..."):
                chat_res = model.generate_content(f"ในฐานะ BHOON KHARN AI วิเคราะห์เชิงลึกจากคำถามนี้: {prompt_chat}")
                st.markdown(chat_res.text)
                st.session_state.full_report += f"\n\nคำถาม: {prompt_chat}\nคำตอบ: {chat_res.text}"
        st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์นี้เป็นเพียงการสังเกตการณ์เบื้องต้น โปรดปรึกษาวิศวกรของท่านเพื่อความถูกต้อง")
