import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import time

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; }
    .owner-box { background-color: #f0f4f8; border-left: 5px solid #1E3A8A; padding: 18px; border-radius: 5px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (เน้นรุ่น Flash เพื่อเลี่ยง Quota เต็ม) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "❌ ไม่พบ API Key"
    
    try:
        genai.configure(api_key=api_key)
        
        # ค้นหา Model ที่โควตาเยอะที่สุด (1.5-flash)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # บังคับเลือก Flash ก่อน Pro เพราะโควตาฟรีของ Pro น้อยมาก
        selected_m = None
        priority_list = ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest", "models/gemini-2.0-flash-exp"]
        
        for p in priority_list:
            if p in available_models:
                selected_m = p
                break
        
        if not selected_m:
            selected_m = available_models[0] if available_models else "models/gemini-1.5-flash"

        model = genai.GenerativeModel(model_name=selected_m)
        return model, f"✅ พร้อมใช้งาน (รุ่นประหยัดโควตา: {selected_m})"
        
    except Exception as e:
        return None, f"❌ ข้อผิดพลาด: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

for k in ["chat_history", "analysis_result", "suggested_qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "analysis_result" else ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    st.info(st.session_state.status)
    if st.button("🔄 ล้าง Error / เชื่อมต่อใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("มุมมองการวิเคราะห์:", ["📊 เทคนิค", "🏠 เจ้าของบ้าน"])

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน", type=['jpg','jpeg','png'])
    if bp: st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 5. LOGIC ---
def run_analysis():
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน")
        return

    with st.spinner("AI กำลังวิเคราะห์ (อาจใช้เวลา 10-20 วินาที)..."):
        try:
            p = f"วิเคราะห์ภาพงานก่อสร้างนี้ในฐานะวิศวกร (โหมด: {mode}) สรุปหัวข้อ [ANALYSIS], [RISK], [STANDARD], [OWNER_NOTE] และถามช่าง: 3 ข้อ"
            inps = [p]
            if bp: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            response = st.session_state.engine.generate_content(inps)
            txt = response.text
            
            st.session_state.suggested_qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.analysis_result = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            
        except Exception as e:
            err = str(e)
            if "429" in err:
                st.error("⚠️ โควตาเต็มชั่วคราว! กรุณารอประมาณ 30 วินาทีแล้วกดปุ่มวิเคราะห์อีกครั้งครับ (เนื่องจากรุ่นฟรีมีการจำกัดจำนวนครั้งการกด)")
            else:
                st.error(f"การวิเคราะห์ล้มเหลว: {err}")

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาแนบรูปภาพ")

if st.session_state.analysis_result:
    st.divider()
    res = st.session_state.analysis_result
    for tit, tag in [("🔍 วิเคราะห์", "[ANALYSIS]"), ("⏱️ จุดเสี่ยง", "[RISK]"), ("🏗️ มาตรฐาน", "[STANDARD]"), ("🏠 เจ้าของบ้าน", "[OWNER_NOTE]")]:
        if tag in res:
            cont = res.split(tag)[1].split("[")[0].strip()
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-box'><b>{tit}</b><br>{cont}</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{tit}**", expanded=True if tag=="[ANALYSIS]" else False): st.write(cont)

    if st.session_state.suggested_qs:
        st.write("---")
        cols = st.columns(len(st.session_state.suggested_qs))
        for i, q in enumerate(st.session_state.suggested_qs):
            if cols[i].button(f"💬 {q}", key=f"b_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": q})
                res_q = st.session_state.engine.generate_content(f"ตอบในฐานะ BHOON KHARN AI: {q}")
                st.session_state.chat_history.append({"role": "assistant", "content": res_q.text})
                st.rerun()

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if u_i := st.chat_input("ถามเพิ่มเติม..."):
        st.session_state.chat_history.append({"role": "user", "content": u_i})
        res_i = st.session_state.engine.generate_content(f"ในฐานะ BHOON KHARN AI: {u_i}")
        st.session_state.chat_history.append({"role": "assistant", "content": res_i.text})
        st.rerun()
