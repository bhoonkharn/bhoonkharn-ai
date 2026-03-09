import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN AI
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบดึง API Key จาก Secrets
def get_all_api_keys():
    try:
        keys = []
        if "GOOGLE_API_KEY" in st.secrets:
            keys.append(st.secrets["GOOGLE_API_KEY"])
        for key in st.secrets:
            if "GOOGLE_API_KEY" in key and st.secrets[key] not in keys:
                keys.append(st.secrets[key])
        return keys
    except:
        return []

all_keys = get_all_api_keys()

# 3. ฟังก์ชันโหลดโมเดลแบบห้ามตาย (Robust Connection)
@st.cache_resource
def initialize_bhoonkharn_ai(keys):
    if not keys:
        return None, "ไม่พบ API Key ในระบบ Secrets"
    
    random_keys = keys.copy()
    random.shuffle(random_keys)
    
    for key in random_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            # ทดสอบเรียกสั้นๆ เพื่อยืนยันว่า Key ใช้งานได้
            model.generate_content("test") 
            return model, "Success"
        except:
            continue
    return None, "กุญแจทั้งหมดไม่สามารถใช้งานได้"

# ตรวจสอบการเชื่อมต่อ
if "active_model" not in st.session_state or st.session_state.active_model is None:
    model, status = initialize_bhoonkharn_ai(all_keys)
    st.session_state.active_model = model
    st.session_state.conn_status = status

model = st.session_state.active_model

# ระบบ Session สำหรับเก็บประวัติ
if "messages" not in st.session_state: st.session_state.messages = []
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "suggested_questions" not in st.session_state: st.session_state.suggested_questions = []

# 4. แถบเครื่องมือทางซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if model:
        st.success("🟢 สถานะ: เชื่อมต่อสำเร็จ")
    else:
        st.error(f"🔴 สถานะ: {st.session_state.conn_status}")
        if st.button("🔄 พยายามเชื่อมต่อใหม่"):
            st.session_state.active_model = None
            st.rerun()
            
    st.divider()
    analysis_mode = st.radio("รูปแบบรายงาน:", ["📊 ข้อมูลทางเทคนิคเชิงลึก", "🏠 สรุปประเด็นสำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติงานนี้", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.session_state.suggested_questions = []
        st.rerun()

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุอ้างอิง", type=['jpg', 'png', 'jpeg'])
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริงที่ต้องการตรวจ", type=['jpg', 'png', 'jpeg'])

# ฟังก์ชันจัดการคำถาม (ทั้งพิมพ์เองและปุ่มกด)
def ask_bhoonkharn(query):
    if not model:
        st.error("AI ไม่พร้อมใช้งาน")
        return
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"): 
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์เชิงลึก..."):
            res = model.generate_content(f"ตอบคำถามเชิงลึกในฐานะ BHOON KHARN: {query}")
            st.markdown(res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {res.text}"
            st.session_state.messages.append({"role": "assistant", "content": res.text})

# 6. ปุ่มเริ่มวิเคราะห์ (จุดที่เคยเกิด Indentation Error)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not model:
        st.error("กรุณาเชื่อมต่อ AI ก่อนเริ่มงาน")
    elif site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                # Prompt แบบ Direct ไม่แนะนำตัว
                prompt = f"""
                ห้ามแนะนำตัว ห้ามทักทาย ให้เริ่มรายงานทันทีดังนี้:
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
                st.rerun()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนเริ่มวิเคราะห์")

# 7. แสดงผลรายงานและปุ่ม Quick Reply
