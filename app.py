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

# 2. ระบบดึง API Key จาก Secrets (ตรวจสอบอย่างละเอียด)
def get_all_api_keys():
    try:
        # พยายามดึง keys ทั้งแบบเดี่ยวและแบบหลายตัว
        keys = []
        if "GOOGLE_API_KEY" in st.secrets:
            keys.append(st.secrets["GOOGLE_API_KEY"])
        
        # ดึง keys อื่นๆ ที่อาจจะตั้งชื่อเป็น GOOGLE_API_KEY_1, _2...
        for key in st.secrets:
            if "GOOGLE_API_KEY" in key and st.secrets[key] not in keys:
                keys.append(st.secrets[key])
        return keys
    except:
        return []

all_keys = get_all_api_keys()

# 3. ฟังก์ชันโหลดโมเดลแบบ "ห้ามตาย" (Auto-Retry System)
def initialize_bhoonkharn_ai():
    if not all_keys:
        return None, "ไม่พบ API Key ในระบบ Secrets"
    
    # สุ่มกุญแจมาลองใช้งาน
    random.shuffle(all_keys)
    for key in all_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            # ทดสอบเรียกสั้นๆ เพื่อยืนยันว่า Key นี้ใช้งานได้จริง
            model.generate_content("ping") 
            return model, "Success"
        except Exception as e:
            continue # ถ้ากุญแจนี้เสีย ให้ลองตัวถัดไป
    
    return None, "กุญแจทั้งหมดในระบบไม่สามารถใช้งานได้ (Invalid or Quota Exceeded)"

# เก็บ Model ไว้ใน Session เพื่อไม่ต้องโหลดใหม่ทุกครั้งที่กดปุ่ม
if "active_model" not in st.session_state or st.session_state.active_model is None:
    model, status = initialize_bhoonkharn_ai()
    st.session_state.active_model = model
    st.session_state.conn_status = status

model = st.session_state.active_model

# --- ระบบ Session ข้อมูล ---
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
        if st.button("🔄 พยายามเชื่อมต่อใหม่อีกครั้ง", use_container_width=True):
            st.session_state.active_model, st.session_state.conn_status = initialize_bhoonkharn_ai()
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

def ask_bhoonkharn(query):
    if not model:
        st.error("AI ไม่พร้อมใช้งานในขณะนี้")
        return
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"): st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์..."):
            res = model.generate_content(f"ในฐานะผู้เชี่ยวชาญ BHOON KHARN วิเคราะห์เชิงลึก: {query}")
            st.markdown(res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {res.text}"
            st.session_state.messages.append({"role": "assistant", "content": res.text})

# 6. เริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not model:
        st.error(f"ไม่สามารถเริ่มงานได้: {st.session_state.conn_status}")
    elif site_file or blue_file:
