import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: ปรับขนาดตัวหนังสือส่วนถามต่อให้เล็กและได้สัดส่วน
st.markdown("""
    <style>
    .disclaimer-text {
        color: #8B0000; /* สีแดงเลือดหมู */
        font-size: 0.8rem;
        line-height: 1.4;
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    .check-box {
        padding: 5px 0 5px 20px;
        border-left: 4px solid #1E3A8A;
        margin-bottom: 25px;
        color: #31333F;
        line-height: 1.8;
    }
    /* ปรับปุ่มคำถามให้จิ๋วและสะอาดตา */
    .stButton>button {
        font-size: 0.7rem !important; 
        padding: 1px 8px !important;
        min-height: 24px !important;
        height: 24px !important;
        border-radius: 4px !important;
        color: #666 !important;
        border: 1px solid #eee !important;
    }
    /* ปรับหัวข้อถามต่อให้เล็กลงและไม่เด่นเกินไป */
    .quick-q-label {
        font-size: 0.7rem !important;
        color: #999 !important;
        margin-bottom: 8px !important;
        margin-top: 20px !important;
        font-weight: normal !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการ API Key
def get_working_keys():
    keys = []
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "GOOGLE_API_KEY" in k and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "ไม่พบ API Key"
    shuffled = keys.copy()
    random.shuffle(shuffled)
    for k in shuffled:
        try:
            genai.configure(api_key=k)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0] if models else None
            if not target: continue
            model = genai.GenerativeModel(target)
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    engine, status = init_engine(get_working_keys())
    st.session_state.engine = engine
    st.session_state.status = status

# ระบบ Session ข้อมูล
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar แถบซ้าย
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if st.session_state.engine: st.success("🟢 ระบบพร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status', 'ขัดข้อง')}")
    
    if st.button("🔄 รีเซ็ตระบบ"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดและพรีวิวรูปภาพ
col_l, col_r = st.columns(2)
with col_
