import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 5px; }
    .owner-box { background-color: #f0f4f8; border-left: 5px solid #1E3A8A; padding: 18px; border-radius: 5px; margin: 10px 0; }
    .footer-note { color: #8B0000; font-size: 0.75rem; text-align: center; margin-top: 50px; opacity: 0.7; border-top: 1px solid #eee; padding-top: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบแก้ปัญหา 404 แบบเจาะลึก) ---
def get_api_key():
    if "GOOGLE_API_KEY" in st.secrets: return st.secrets["GOOGLE_API_KEY"]
    for k in st.secrets.keys():
        if "API_KEY" in k.upper(): return st.secrets[k]
    return None

def init_ai_engine():
    api_key = get_api_key()
    if not api_key: return None, "❌ ไม่พบ API Key"
    
    try:
        genai.configure(api_key=api_key)
        
        # ค้นหาชื่อ Model ที่ใช้งานได้จริงในเครื่องนี้ (แก้ปัญหา 404 โดยตรง)
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except:
            # ถ้า list_models ไม่ได้ ให้ใช้ชื่อมาตรฐานที่น่าจะผ่าน
            available_models = ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest", "models/gemini-pro-vision"]

        # เลือกตัวแรกที่เจอ หรือตัวที่เสถียรที่สุด
        target_model = "models/gemini-1.5-flash" 
        if any("1.5-flash" in m for m in available_models):
            target_model = [m for m in available_models if "1.5-flash" in m][0]
        elif available_models:
            target_model = available_models[0]

        model = genai.GenerativeModel(target_model)
        return model, f"✅ เชื่อมต่อสำเร็จ ({target_model})"
        
    except Exception as e:
        return None, f"❌ ข้อผิดพลาด: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analysis_result" not in st.session_state: st.session_state.analysis_result = ""
if "suggested_qs" not in st.session_state: st.session_state.suggested_qs = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ Settings")
    st.info(st.session_state.status)
    if st.button("🔄 ลองเชื่อมต่อใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("มุมมองการวิเคราะห์:", ["📊 เชิงเทคนิค", "🏠 สำหรับเจ้าของบ้าน"])

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 รูปแบบแปลน", type=['jpg','jpeg','png'])
    if bp: st.image(bp)
with c2:
    site = st.file_uploader("📸 รูปหน้างานจริง", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 5. LOGIC ---
def run_analysis():
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน")
        return

    with st.spinner("กำลังวิเคราะห์..."):
        try:
            prompt = f"วิเคราะห์ภาพงานก่อสร้างนี้ในโหมด {mode} โดยแบ่งหัวข้อ [ANALYSIS], [RISK], [STANDARD], [OWNER_NOTE] และจบด้วย 'ถามช่าง: ' 3 ข้อ"
            
            payload = [prompt]
            if bp: payload.append(Image.open(bp))
            if site: payload.append(Image.open(site))
            
            response = st.session_state.engine.generate_content(payload)
            txt = response.text
            
            st.session_state.suggested_qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.analysis_result = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def ask_more(q):
    if st.session_state.engine:
        res = st.session_state.engine.generate_content(f"ในฐานะ BHOON KHARN AI: {q}")
        st.session_state.chat_history.append({"role": "user", "content": q})
        st.session_state.chat_history.append({"role": "assistant", "content": res.text})

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาแนบรูปภาพ")

if st.session_state.analysis_result:
    st.divider()
    res = st.session_state.analysis_result
    for title, tag in [("🔍 วิเคราะห์", "[ANALYSIS]"), ("⏱️ จุดเสี่ยง", "[RISK]"), ("🏗️ มาตรฐาน", "[STANDARD]"), ("🏠 แนะนำเจ้าของบ้าน", "[OWNER_NOTE]")]:
        if tag in res:
            cont = res.split(tag)[1].split("[")[0].strip()
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-box'><b>{title}</b><br>{cont}</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{title}**", expanded=True): st.write(cont)

    if st.session_state.suggested_qs:
        st.write("---")
        cols = st.columns(len(st.session_state.suggested_qs))
        for i, q in enumerate(st.session_state.suggested_qs):
            if cols[i].button(f"💬 {q}", key=f"b_{i}"):
                ask_more(q)
                st.rerun()

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if u_i := st.chat_input("ถามเพิ่มเติม..."):
        ask_more(u_i)
        st.rerun()

st.markdown("<div class='footer-note'>ประเมินเบื้องต้นจากรูปเท่านั้น</div>", unsafe_allow_html=True)
