import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN AI
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ระบบวิเคราะห์หน้างานและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ API Key และการโหลดโมเดล
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ Secrets กรุณาตั้งค่า GOOGLE_API_KEY")
    st.stop()

@st.cache_resource
def get_bhoonkharn_ai(api_key):
    try:
        genai.configure(api_key=api_key)
        # ระบุชื่อรุ่นโดยตรงเพื่อความเสถียร (ใช้ gemini-1.5-flash)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # ทดสอบการเรียกใช้งานสั้นๆ เพื่อเช็คว่า Key ใช้ได้จริงไหม
        model.generate_content("test") 
        return model
    except Exception as e:
        return None

# สุ่ม Key จนกว่าจะได้ตัวที่ใช้งานได้
if "active_model" not in st.session_state:
    selected_key = random.choice(all_keys)
    st.session_state.active_model = get_bhoonkharn_ai(selected_key)

model = st.session_state.active_model

# --- ระบบ Session สำหรับเก็บประวัติ ---
if "messages" not in st.session_state: st.session_state.messages = []
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "suggested_questions" not in st.session_state: st.session_state.suggested_questions = []

# 3. เครื่องมือทางด้านซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if model:
        st.success("สถานะระบบ: พร้อมใช้งาน")
    else:
        st.error("สถานะระบบ: เชื่อมต่อล้มเหลว")
        if st.button("🔄 พยายามเชื่อมต่อใหม่"):
            st.session_state.active_model = get_bhoonkharn_ai(random.choice(all_keys))
            st.rerun()
            
    st.divider()
    analysis_mode = st.radio(
        "รูปแบบรายงาน:",
        ["📊 ข้อมูลทางเทคนิคเชิงลึก", "🏠 สรุปประเด็นสำหรับเจ้าของบ้าน"]
    )
    
    if st.button("🗑️ เริ่มการตรวจสอบใหม่", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.session_state.suggested_questions = []
        st.rerun()

# 4. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุอ้างอิง", type=['jpg', 'png', 'jpeg'])
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริงที่ต้องการตรวจ", type=['jpg', 'png', 'jpeg'])

# ฟังก์ชันช่วยในการถามต่อ
def ask_bhoonkharn(query):
    if not model:
        st.error("โมเดลไม่พร้อมใช้งาน")
        return
    
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์ข้อมูล..."):
            res = model.generate_content(f"ในฐานะผู้เชี่ยวชาญ BHOON KHARN วิเคราะห์เชิงลึกจากคำถามนี้: {query}")
            st.markdown(res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {res.text}"
            st.session_state.messages.append({"role": "assistant", "content": res.text})

# 5. เริ่มการวิเคราะห์หลัก
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not model:
        st.error("ไม่สามารถเริ่มงานได้ เนื่องจากเชื่อมต่อ AI ไม่สำเร็จ")
    elif site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                prompt = f"""
                ห้ามแนะนำตัว ห้ามทักทาย ห้ามทวนคำสั่ง ให้เริ่มรายงานทันทีดังนี้:

                🔍 [วิเคราะห์หน้างาน]: ระบุหมวดงานและสถานะ
                ⚠️ [ผลกระทบต่อเนื่อง]: Domino Effect และผลเสียต่องบประมาณ
                🏗️ [มาตรฐานเทคนิค]: มาตรฐานเชิงลึกและปัจจัยเรื่องเวลา/อายุวัสดุ
                🏠 [มุมเจ้าของบ้าน]: วิธีตรวจเช็คเอง 1-2-3 (ภาษาง่ายๆ)
                💬 [คำถามชวนคุยต่อ]: แนะนำ 3 คำถามสำคัญที่ขึ้นต้นด้วย 'ถามช่าง:'
                
                รูปแบบ: {analysis_mode}
                """
                
                imgs = [Image.open(f) for f in [blue_file, site_file] if f]
                response = model.generate_content([prompt] + imgs)
                
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
                # ดึงคำถามมาทำปุ่ม
                questions = re.findall(r"ถามช่าง: (.+)", response.text)
                st.session_state.suggested_questions = [q.strip() for q in questions[:3]]
                st.rerun() # Refresh เพื่อให้ปุ่มแสดงผลทันที
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 6. แสดงรายงานและปุ่ม Quick Reply
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์หน้างาน")
    
    st.download_button("📥 บันทึกรายงาน", data=st.session_state.full_report, file_name="BHOON_KHARN_Report.txt")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ปุ่มถามต่อ
    if st.session_state.suggested_questions:
        st.info("💡 **สอบถามรายละเอียดเพิ่มได้ทันที:**")
        for q in st.session_state.suggested_questions:
            if st.button(f"🔎 {q}", key=f"q_{hash(q)}", use_container_width=True):
                ask_bhoonkharn(q)
                st.rerun()

    if prompt_chat := st.chat_input("พิมพ์คำถามอื่นๆ..."):
        ask_bhoon
