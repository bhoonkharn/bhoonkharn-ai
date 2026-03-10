import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. Branding & UI (เป๊ะตามสเปกที่คุยกันไว้)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    .owner-box { border-left: 5px solid #1E3A8A; padding-left: 20px; margin-bottom: 25px; color: #31333F !important; line-height: 1.8; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border: 1px solid #eee !important; }
    .maroon-note { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 40px; padding-top: 10px; }
</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

# 2. Key Discovery (ฟังก์ชันค้นหา Key ใน Secrets)
def discover_keys():
    found_keys = []
    # ตรวจสอบตัวแปรมาตรฐาน
    if "GOOGLE_API_KEY" in st.secrets:
        found_keys.append(st.secrets["GOOGLE_API_KEY"])
    # กวาดหาตัวแปรที่ชื่อมีคำว่า API_KEY
    for k in st.secrets.keys():
        if "API_KEY" in k.upper() and st.secrets[k] not in found_keys:
            found_keys.append(st.secrets[k])
    return found_keys

# 3. Engine (พร้อมระบบแจ้งเตือน Error จริง)
@st.cache_resource
def init_engine(keys):
    if not keys: return None, "❌ ไม่พบ API Key ใน Secrets (ตรวจสอบชื่อตัวแปร)"
    random.shuffle(keys)
    # พยายามใช้รุ่น 1.5 เป็นหลักเพื่อเลี่ยง Quota 2.0 ที่เต็มไวมาก
    models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash"]
    
    last_error = ""
    for pk in keys:
        genai.configure(api_key=pk)
        for m_name in models:
            try:
                m = genai.GenerativeModel(m_name)
                m.generate_content("ping")
                return m, f"🟢 {m_name} พร้อมใช้งาน"
            except Exception as e:
                last_error = str(e)
                continue
    return None, f"❌ เข้าถึงไม่ได้: {last_error[:100]}"

# เรียกใช้งาน Engine
all_keys = discover_keys()
if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(all_keys)

# ประวัติสนทนา
for k in ["chat", "report", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "report" else ""

# 4. Sidebar Diagnostic (พี่ Nhum ดูตรงนี้เพื่อเช็กสถานะ)
with st.sidebar:
    st.header("⚙️ ระบบตรวจสอบ")
    st.write(f"🔑 พบ Key ทั้งหมด: **{len(all_keys)}** ตัว")
    if st.session_state.engine: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    
    if st.button("🔄 รีเซ็ตและสุ่ม Key ใหม่"):
        st.session_state.engine = None
        st.rerun()
    
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
        st.session_state.chat, st.session_state.report, st.session_state.qs = [], "", []
        st.rerun()

# 5. UI Layout
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg','png','jpeg'])
    if bp: st.image(bp, use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg','png','jpeg'])
    if site: st.image(site, use_container_width=True)

def run_chat(q):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("ในฐานะ BHOON KHARN AI: " + q)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 6. Analysis Execution
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('กำลังวิเคราะห์...'):
            try:
                p = f"Analyze as BHOON KHARN AI advisor. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (
