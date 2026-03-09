import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random
import re

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ระบบวิเคราะห์หน้างานและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ API Key
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()

# 3. โหลดโมเดล
@st.cache_resource
def load_model(api_key):
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m.name for m in available_models if 'flash' in m.name.lower()]
        return genai.GenerativeModel(flash_models[0] if flash_models else available_models[0])
    except:
        return None

model = load_model(random.choice(all_keys))

# --- ระบบ Session สำหรับเก็บประวัติ ---
if "messages" not in st.session_state: st.session_state.messages = []
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "suggested_questions" not in st.session_state: st.session_state.suggested_questions = []

# 4. Sidebar
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    analysis_mode = st.radio("รูปแบบรายงาน:", ["📊 ข้อมูลทางเทคนิคเชิงลึก", "🏠 สรุปประเด็นสำหรับเจ้าของบ้าน"])
    if st.button("🗑️ เริ่มการตรวจสอบใหม่"):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.session_state.suggested_questions = []
        st.rerun()

# 5. ส่วนอัปโหลด
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุ", type=['jpg', 'png', 'jpeg'])
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])

# --- ฟังก์ชันช่วยเหลือในการถามตอบ ---
def ask_bhoonkharn(query):
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์ข้อมูลเชิงลึก..."):
            chat_res = model.generate_content(f"ในฐานะผู้เชี่ยวชาญ BHOON KHARN วิเคราะห์เชิงลึกจากคำถามนี้: {query}")
            st.markdown(chat_res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {chat_res.text}"
    st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

# 6. ประมวลผลหลัก
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('กำลังรวบรวมข้อมูลตามมาตรฐาน BHOON KHARN...'):
            try:
                # Prompt ที่บังคับรูปแบบคำถามชวนคุยเพื่อให้ระบบดึงออกมาทำปุ่มได้ง่าย
                universal_prompt = f"""
                วิเคราะห์งานก่อสร้างนี้โดยไม่ต้องทักทายหรือแนะนำตัว AI 
                ให้ใช้หัวข้อดังนี้:
                1. 🔍 [การวิเคราะห์หน้างาน]: หมวดงานและสถานะ
                2. ⚠️ [การประเมินผลกระทบต่อเนื่อง]: Domino Effect และผลเสียต่องบประมาณ
                3. 🏗️ [เกณฑ์มาตรฐานวิศวกรรม]: มาตรฐานเชิงลึกและปัจจัยเรื่องเวลา/อายุวัสดุ
                4. 🏠 [สรุปสำหรับเจ้าของบ้าน]: วิธีตรวจเช็คเอง 1-2-3 (ภาษาง่ายๆ)
                5. 💬 [ประเด็นที่ต้องตรวจสอบต่อ]: แนะนำ 3 คำถามสำคัญที่ขึ้นต้นด้วย 'ถามช่าง:' 
                
                รูปแบบ: {analysis_mode}
                """
                
                imgs = [Image.open(f) for f in [blue_file, site_file] if f]
                response = model.generate_content([universal_prompt] + imgs)
                
                # เก็บผลการวิเคราะห์
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
                # ดึงคำถามออกมาทำปุ่ม (มองหาบรรทัดที่ขึ้นต้นด้วย "ถามช่าง:")
                questions = re.findall(r"ถามช่าง: (.+)", response.text)
                st.session_state.suggested_questions = questions[:3]
                
            except Exception as e:
                st.error(f"ระบบขัดข้อง: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผลรายงานและปุ่มคำถาม
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการตรวจสอบโดย BHOON KHARN AI")
    
    # แสดงข้อความแชท
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- ส่วนใหม่: ปุ่มคำถามชวนคุยต่อ (Quick Reply) ---
    if st.session_state.suggested_questions:
        st.markdown
