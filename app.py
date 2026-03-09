import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: เน้นความสะอาดตา สัดส่วนถูกต้อง และสีแดงเลือดหมูตามโจทย์
st.markdown("""
    <style>
    /* ข้อกำหนดการใช้งาน: สีแดงเลือดหมู */
    .disclaimer-text {
        color: #8B0000 !important;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-top: 35px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    /* จุดสังเกตเจ้าของบ้าน: เส้นน้ำเงินด้านซ้าย คลีนๆ ไม่จ้าตา */
    .homeowner-box {
        padding: 5px 0 5px 20px;
        border-left: 4px solid #1E3A8A;
        margin-bottom: 25px;
        color: #31333F;
        line-height: 1.8;
    }
    /* ปรับปุ่มถามต่อให้จิ๋วและสะอาดตาที่สุด */
    div.stButton > button {
        font-size: 0.7rem !important;
        height: 26px !important;
        padding: 0px 10px !important;
        color: #666 !important;
        border-radius: 4px !important;
    }
    /* หัวข้อถามต่อ: เล็กและถ่อมตัว */
    .q-label {
        font-size: 0.7rem;
        color: #999;
        margin-bottom: 8px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการการเชื่อมต่อ (Engine)
def get_all_keys():
    keys = []
    # ค้นหาทุกอย่างที่มีคำว่า API_KEY ใน Secrets
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "API_KEY" in k.upper() and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "ไม่พบ API Key ในระบบ"
    
    # สุ่มลำดับ Key เพื่อกระจายการใช้งาน
    shuffled_keys = keys.copy()
    random.shuffle(shuffled_keys)
    
    for k in shuffled_keys:
        try:
            genai.configure(api_key=k)
            # ใช้รุ่น Flash ที่เสถียรและเร็วที่สุด
            model = genai.GenerativeModel("gemini-1.5-flash")
            # ทดสอบยิง Ping สั้นๆ เพื่อเช็กว่า Key ใช้ได้จริงไหม
            model.generate_content("ping")
            return model, "Ready"
        except Exception:
            continue
    return None, "การเชื่อมต่อล้มเหลว (Key อาจจะเต็มหรือผิด)"

# ตรวจสอบและเริ่ม Engine
if "engine" not in st.session_state:
    engine, status = init_engine(get_all_keys())
    st.session_state.engine = engine
    st.session_state.status = status

# ระบบ Session เก็บข้อมูล
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar แถบด้านซ้าย
with st.sidebar:
    st.header("⚙️ BHOON KHARN AI")
    if st.session_state.engine:
        st.success("🟢 ระบบพร้อมใช้งาน")
    else:
        st.error(f"🔴 {st.session_state.status}")
    
    if st.button("🔄 ลองเชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
        
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ (ประจำที่ด้านบนแน่นอน)
col_l, col_r = st.columns(2)
with col_l:
    blueprint = st.file_uploader("📋 แบบแปลน / สпеกวัสดุ", type=['jpg', 'png', 'jpeg'])
    if blueprint: st.image(blueprint, caption="แบบอ้างอิง", use_container_width=True)

with col_r:
    site_photo = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_photo: st.image(site_photo, caption="หน้างานจริง", use_container_width=True)

# ฟังก์ชันส่งคำถามต่อเนื่อง
def run_query(q):
    if not st.session_state.engine: return
    st.session_state.chat_history.append({"role": "user", "content": q})
    with st.spinner('BHOON KHARN AI กำลังวิเคราะห์...'):
        res = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN AI: " + q)
        st.session_state.chat_history.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine:
        st.error("ไม่สามารถเริ่มงานได้เนื่องจากการเชื่อมต่อล้มเหลว")
    elif site_photo or blueprint:
        with st.spinner('BHOON KHARN AI กำลังตรวจสอบหน้างาน...'):
            try:
                # Prompt: สั่งห้ามใช้ HTML และเน้นความกระชับ
                prompt_text = (
                    "คุณคือที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพนี้โดยเริ่มทันที:\n"
                    "🔍 วิเคราะห์หน้างาน: (ระบุงานและสถานะปัจจุบัน)\n"
                    "⏱️ จุดตายวิกฤต: (ความเสี่ยงแฝงที่ต้องระวัง)\n"
                    "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect และงบประมาณซ่อม)\n"
                    "🏗️ มาตรฐานเทคนิค: (วสท./มยผ./สากล)\n"
                    "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (สรุปเป็นข้อๆ โดยใช้เครื่องหมาย * นำหน้า ห้ามใช้ HTML ห้ามใช้ <br
