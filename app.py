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
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; }
    .owner-box { background-color: #f0f4f8; border-left: 5px solid #1E3A8A; padding: 18px; border-radius: 5px; margin: 10px 0; }
    .footer-note { color: #8B0000; font-size: 0.75rem; text-align: center; margin-top: 50px; opacity: 0.7; border-top: 1px solid #eee; padding-top: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบสุ่มรุ่นและ Fallback อัตโนมัติ) ---
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
        
        # 1. ลองดึงรายชื่อรุ่นที่มีในระบบจริงก่อน
        real_available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    real_available_models.append(m.name)
        except: pass

        # 2. รายชื่อรุ่นที่เรียงจาก ใหม่ -> เก่า (Fallback List)
        # ใส่ชื่อเต็มแบบ 'models/...' เพื่อป้องกัน 404
        fallback_list = [
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-flash",
            "models/gemini-2.0-flash-exp",
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.5-pro",
            "models/gemini-pro-vision"
        ]

        # ผสมรายการที่เจอจริงกับรายการสำรอง (เอาที่เจอจริงขึ้นก่อน)
        final_models = []
        for m in real_available_models:
            if m not in final_models: final_models.append(m)
        for m in fallback_list:
            if m not in final_models: final_models.append(m)

        # 3. ลองเชื่อมต่อทีละตัวจนกว่าจะผ่าน
        for model_name in final_models:
            try:
                # แก้ปัญหา 404 โดยการเช็คชื่อรุ่นให้ชัวร์
                test_model = genai.GenerativeModel(model_name)
                # ลองยิงทดสอบสั้นๆ
                test_model.generate_content("Hi", generation_config={"max_output_tokens": 1})
                return test_model, f"✅ พร้อมใช้งาน (รุ่น: {model_name})"
            except Exception:
                continue # ถ้าพัง ลองตัวถัดไป
                
        return None, "❌ ไม่สามารถเชื่อมต่อกับรุ่นใดๆ ได้เลย (เช็ค API Key ของคุณ)"
        
    except Exception as e:
        return None, f"❌ ข้อผิดพลาดระบบ: {str(e)}"

# ตรวจสอบและสร้าง Engine
if "engine" not in st.session_state or st.session_state.engine is None:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# ค่าเริ่มต้น Session
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analysis_result" not in st.session_state: st.session_state.analysis_result = ""
if "suggested_qs" not in st.session_state: st.session_state.suggested_qs = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    st.info(st.session_state.status)
    if st.button("🔄 สลับรุ่น AI / เชื่อมต่อใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("มุมมองการวิเคราะห์:", ["📊 เชิงเทคนิค", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างหน้าจอ", use_container_width=True):
        st.session_state.chat_history, st.session_state.analysis_result, st.session_state.suggested_qs = [], "", []
        st.rerun()

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แนบแปลน (ถ้ามี)", type=['jpg','jpeg','png'])
    if bp: st.image(bp)
with c2:
    site = st.file_uploader("📸 แนบรูปหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 5. LOGIC ---
def run_analysis():
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน กรุณากดปุ่มลองเชื่อมต่อใหม่ที่เมนูด้านซ้าย")
        return

    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            prompt = f"คุณคือวิศวกรผู้เชี่ยวชาญ วิเคราะห์ภาพในโหมด {mode} สรุปหัวข้อ [ANALYSIS], [RISK], [STANDARD], [OWNER_NOTE] และจบด้วย 'ถามช่าง: ' 3 ข้อ"
            
            payload = [prompt]
            if bp: payload.append(Image.open(bp))
            if site: payload.append(Image.open(site))
            
            response = st.session_state.engine.generate_content(payload)
            txt = response.text
            
            st.session_state.suggested_qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.analysis_result = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            
        except Exception as e:
            st.error(f"การวิเคราะห์ล้มเหลว: {str(e)}")

def ask_more(q):
    if st.session_state.engine:
        try:
            res = st.session_state.engine.generate_content(f"ตอบคำถามในฐานะ BHOON KHARN AI: {q}")
            st.session_state.chat_history.append({"role": "user", "content": q})
            st.session_state.chat_history.append({"role": "assistant", "content": res.text})
        except: st.error("ไม่สามารถตอบคำถามได้ในขณะนี้")

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาใส่รูปภาพก่อนครับ")

if st.session_state.analysis_result:
    st.divider()
    res = st.session_state.analysis_result
    sections = [("🔍 วิเคราะห์", "[ANALYSIS]"), ("⏱️ จุดเสี่ยง", "[RISK]"), ("🏗️ มาตรฐาน", "[STANDARD]"), ("🏠 แนะนำเจ้าของบ้าน", "[OWNER_NOTE]")]
    
    for title, tag in sections:
        if tag in res:
            cont = res.split(tag)[1].split("[")[0].strip()
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-box'><b>{title}</b><br>{cont}</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{title}**", expanded=True if tag=="[ANALYSIS]" else False): st.write(cont)

    if st.session_state.suggested_qs:
        st.write("---")
        st.markdown("**💡 ลองถามต่อ:**")
        cols = st.columns(len(st.session_state.suggested_qs))
        for i, q in enumerate(st.session_state.suggested_qs):
            if cols[i].button(f"💬 {q}", key=f"b_{i}", use_container_width=True):
                ask_more(q)
                st.rerun()

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if u_i := st.chat_input("พิมพ์คำถามเพิ่มเติม..."):
        ask_more(u_i)
        st.rerun()

st.markdown("<div class='footer-note'>ประเมินเบื้องต้นจากภาพเท่านั้น ไม่แทนที่การตรวจโดยวิศวกรวิชาชีพ</div>", unsafe_allow_html=True)
