import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. การตั้งค่าหน้าเว็บและ Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: เน้นคลีน สบายตา สัดส่วนปุ่มจิ๋ว และสีแดงเลือดหมู
st.markdown("""
    <style>
    .disclaimer { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 10px; margin-top: 30px; }
    .owner-box { border-left: 5px solid #1E3A8A; padding-left: 20px; margin-bottom: 20px; line-height: 1.8; color: #31333F; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border: 1px solid #eee !important; border-radius: 4px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ Engine (ใช้รุ่นล่าสุด 2026 ที่เสถียรที่สุด)
def get_keys():
    k = []
    if "GOOGLE_API_KEY" in st.secrets: k.append(st.secrets["GOOGLE_API_KEY"])
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
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())

if "chat" not in st.session_state: st.session_state.chat = []
if "report" not in st.session_state: st.session_state.report = ""
if "qs" not in st.session_state: st.session_state.qs = []

# 3. Sidebar (เมนูการตั้งค่า)
with st.sidebar:
    st.header("⚙️ ระบบ BHOON KHARN")
    if st.session_state.engine: st.success("🟢 AI พร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status', 'ขัดข้อง')}")
    if st.button("🔄 เชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("โหมดรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.report, st.session_state.qs = [], "", []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
    if bp: st.image(bp, caption="Ref", use_container_width=True)
with c2:
    site = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site: st.image(site, caption="Site", use_container_width=True)

def run_q(q_val):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q_val})
    res = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN AI: " + q_val)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มวิเคราะห์ (ตำแหน่งคงที่)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                p = "คุณคือที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพนี้โดยเริ่มทันทีที่หัวข้อแรก:\n"
                p += "🔍 วิเคราะห์หน้างาน: (ระบุงานและสถานะ)\n"
                p += "⏱️ จุดตายวิกฤต: (ระบุความเสี่ยง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect)\n"
                p += "🏗️ มาตรฐานเทคนิค: (วสท./มยผ.)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (เป็นข้อๆ * นำหน้า ห้ามใช้ HTML)\n"
                p += "ท้ายรายงานแนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:' โหมด: " + mode
                
                inputs = [p]
