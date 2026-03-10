import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# --- 1. CONFIG & STYLE (UI ที่สมบูรณ์แบบ: ตัวหนังสือไม่ทับ, Clean Look) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.8; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 30px; }
    .section-header { color: #1E3A8A; font-size: 1.2rem; font-weight: 700; margin-top: 25px; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .owner-content { border-left: 5px solid #1E3A8A; padding-left: 20px; margin: 20px 0; background: transparent !important; color: #31333F !important; font-size: 1rem; }
    div.stButton > button { font-size: 0.75rem !important; border-radius: 10px !important; color: #555 !important; }
    .maroon-note { color: #8B0000; font-size: 0.85rem; border-top: 1px solid #eee; margin-top: 40px; padding-top: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบสุ่มรุ่น AI และ Fallback จากใหม่ไปเก่า - ชุดที่ไม่มีปัญหา) ---
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
        
        # ดึงรายชื่อรุ่นที่มีในระบบจริง
        real_available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    real_available_models.append(m.name)
        except: pass

        # รายชื่อรุ่นสำรอง เรียงจาก ใหม่ -> เก่า
        fallback_list = [
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-flash",
            "models/gemini-2.0-flash-exp",
            "models/gemini-1.5-pro-latest",
            "models/gemini-pro-vision"
        ]

        # รวมและเรียงลำดับรุ่น
        final_models = []
        for m in real_available_models:
            if m not in final_models: final_models.append(m)
        for m in fallback_list:
            if m not in final_models: final_models.append(m)

        # สุ่มและไล่หาตัวที่ใช้งานได้จริง (เพื่อเลี่ยง 404 และ Quota เต็ม)
        for model_name in final_models:
            try:
                test_model = genai.GenerativeModel(model_name)
                test_model.generate_content("Hi", generation_config={"max_output_tokens": 1})
                return test_model, "✅ เชื่อมต่อสำเร็จ"
            except: continue
                
        return None, "❌ ไม่สามารถเชื่อมต่อกับรุ่นใดๆ ได้"
    except Exception as e:
        return None, f"❌ ข้อผิดพลาด: {str(e)}"

if "engine" not in st.session_state or st.session_state.engine is None:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    if "สำเร็จ" in st.session_state.status: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    if st.button("🔄 สลับรุ่น AI / เชื่อมต่อใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("มุมมองการแสดงผล:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติงานตรวจ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนก่อสร้าง", type=['jpg','jpeg','png'])
    if bp: st.image(bp)
with c2:
    site = st.file_uploader("📸 สภาพหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 5. LOGIC ---
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            prompt = f"""วิเคราะห์ภาพในฐานะ BHOON KHARN AI โหมด: {mode}
            หัวข้อ:
            [ANALYSIS] สรุปการวิเคราะห์หน้างานปัจจุบัน
            [RISK] จุดวิกฤตหรือสิ่งที่ต้องระวังเป็นพิเศษ
            [STANDARD] มาตรฐานงานช่างและวิศวกรรม
            [OWNER_NOTE] คำแนะนำสำคัญถึงเจ้าของบ้านและสิ่งที่ควรรู้เกี่ยวกับงานขั้นตอนถัดไป
            และคำแนะนำ 3 ข้อ โดยขึ้นต้นว่า 'ถามช่าง: ' ทุกข้อ"""
            inps = [prompt]
            if bp: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            res = st.session_state.engine.generate_content(inps)
            txt = res.text
            st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.rep = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            st.session_state.chat = []
        except Exception as e: st.error(str(e))

def ask_more(query):
    if st.session_state.engine:
        res = st.session_state.engine.generate_content(f"BHOON KHARN AI: {query}")
        st.session_state.chat.append({"role": "user", "content": query})
        st.session_state.chat.append({"role": "assistant", "content": res.text})

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

if st.session_state.rep:
    st.divider()
    res = st.session_state.rep
    sections = [("🔍 สรุปการวิเคราะห์หน้างาน", "[ANALYSIS]"), ("⏱️ จุดวิกฤตที่ต้องตรวจสอบ", "[RISK]"), ("🏗️ มาตรฐานงานช่างและวิศวกรรม", "[STANDARD]"), ("🏠 สิ่งที่เจ้าของบ้านต้องทราบ (รวมงานต่อเนื่อง)", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in res:
            content = res.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)

    if st.session_state.qs:
        st.write("")
        st.markdown("<p style='font-size:0.85rem; font-weight:bold; color:#1E3A8A;'>💡 ถาม BHOON KHARN AI ต่อ:</p>", unsafe_allow_html=True)
        qcols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if qcols[i].button("🔎 " + qv, key=f"bkq_{i}", use_container_width=True):
                ask_more(qv)
                st.rerun()

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if ui := st.chat_input("สอบถามเพิ่มเติม..."):
        ask_more(ui)
        st.rerun()

    st.markdown("<div class='maroon-note'><strong>หมายเหตุ:</strong> การประเมินนี้ทำโดยวิศวกรรม AI จากรูปภาพเบื้องต้นเท่านั้น ข้อมูลนี้ไม่สามารถนำไปใช้อ้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
