import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บและ Branding (สไตล์ BHOON KHARN)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
    <style>
    /* หมายเหตุสีแดงเลือดหมูท้ายรายงาน */
    .disclaimer-maroon { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 10px; margin-top: 30px; }
    
    /* กล่องเจ้าของบ้าน: เส้นน้ำเงินด้านซ้าย คลีนๆ */
    .owner-section { border-left: 5px solid #1E3A8A; padding-left: 20px; margin-bottom: 20px; line-height: 1.8; color: #31333F; }
    
    /* ปรับขนาดปุ่มถามต่อให้จิ๋วและสะอาดตา */
    div.stButton > button { font-size: 0.7rem !important; height: 24px !important; color: #666 !important; border: 1px solid #eee !important; border-radius: 4px !important; }
    
    /* หัวข้อถามต่อ: สีเทาจาง ขนาดเล็กพิเศษ */
    .q-label-subtle { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ Engine (ตรวจเช็ก API Key)
def get_keys():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for s_key in st.secrets.keys():
        if "API_KEY" in s_key.upper() and st.secrets[s_key] not in k: k.append(st.secrets[s_key])
    return k

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "ไม่พบ API Key"
    random.shuffle(keys)
    for pk in keys:
        try:
            genai.configure(api_key=pk)
            # ใช้รุ่นที่เสถียรที่สุดในปี 2026
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())

# Session States
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "report" not in st.session_state: st.session_state.report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar เมนูด้านซ้าย
with st.sidebar:
    st.header("⚙️ Settings")
    if st.session_state.engine: st.success("🟢 พร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.status}")
    if st.button("🔄 เชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat_history, st.session_state.report, st.session_state.quick_qs = [], "", []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ (ประจำตำแหน่งคงที่)
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
    if bp: st.image(bp, caption="Ref", use_container_width=True)
with c2:
    site = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png
