import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. UI Setup (ปุ่ม 0.7rem, เส้นน้ำเงิน, หมายเหตุแดงเลือดหมู)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    .owner { border-left: 5px solid #1E3A8A; padding-left: 20px; margin-bottom: 25px; color: #31333F !important; line-height: 1.8; }
    .q-lbl { font-size: 0.7rem; color: #999; margin-top: 15px; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border: 1px solid #eee !important; }
    .maroon { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 40px; padding-top: 10px; }
</style>""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h2>", unsafe_allow_html=True)

# 2. Engine (Key Rotation & Fallback)
def get_ks():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for s in st.secrets.keys():
        if "API_KEY" in s.upper() and st.secrets[s] not in k: k.append(st.secrets[s])
    return k

@st.cache_resource
def init_ai(ks):
    if not ks: return None, "No API Key"
    random.shuffle(ks)
    models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash"]
    for pk in ks:
        genai.configure(api_key=pk)
        for m_n in models:
            try:
                m = genai.GenerativeModel(m_n)
                m.generate_content("ping")
                return m, f"Online ({m_n})"
            except: continue
    return None, "Quota Full"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai(get_ks())
for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# 3. Sidebar & Uploaders
with st.sidebar:
    st.header("⚙️ Settings")
    st.write(f"Keys: {len(get_ks())}")
    if st.session_state.engine: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    if st.button("🔄 Reconnect"): st.session_state.engine = None; st.rerun()
    mode = st.radio("Mode:", ["📊 เทคนิค", "🏠 เจ้าของบ้าน"])
    if st.button("🗑️ Clear All"):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน", type=['jpg','png','jpeg'])
    if bp: st.image(bp, use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','png','jpeg'])
    if site: st.image(site, use_container_width=True)

def run_q(q):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("BHOON KHARN AI: " + q)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 4. Analysis Execution
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ
