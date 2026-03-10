import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.8; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 30px; }
    .section-header { color: #1E3A8A; font-size: 1.2rem; font-weight: 700; margin-top: 25px; margin-bottom: 5px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .owner-content { border-left: 5px solid #1E3A8A; padding-left: 20px; margin: 15px 0; background: transparent !important; color: inherit !important; }
    div.stButton > button { font-size: 0.75rem !important; border-radius: 10px !important; }
    .maroon-note { color: #8B0000; font-size: 0.85rem; border-top: 1px solid #eee; margin-top: 40px; padding: 20px 0; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบค้นหารุ่นที่ใช้งานได้จริง เพื่อแก้ 404) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "❌ ไม่พบ API Key"
    
    try:
        genai.configure(api_key=api_key)
        
        # ค้นหาว่า ณ วินาทีนี้ Google ยอมให้ใช้รุ่นไหนบ้าง (ป้องกัน 404)
        valid_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                valid_models.append(m.name)
        
        if not valid_models:
            return None, "❌ ไม่พบรุ่น AI ที่รองรับในบัญชีนี้"

        # เลือกตัวที่เหมาะสมที่สุดจากลิสต์ที่มีอยู่จริง
        best_m = ""
        # ลำดับความสำคัญ: 1.5-flash -> 2.0-flash -> 1.5-pro -> ตัวแรกที่เจอ
        for target in ["1.5-flash", "2.0-flash", "1.5-pro", "gemini-pro"]:
            for actual in valid_models:
                if target in actual:
                    best_m = actual
                    break
            if best_m: break
        
        if not best_m: best_m = valid_models[0]

        model = genai.GenerativeModel(model_name=best_m)
        return model, f"✅ เชื่อมต่อสำเร็จ (ใช้: {best_m})"
        
    except Exception as e:
        return None, f"❌ การเชื่อมต่อขัดข้อง: {str(e)}"

# ตรวจสอบ Engine
if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    st.info(st.session_state.status)
    if st.button("🔄 รีเซ็ตและค้นหา Model ใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("มุมมองการแสดงผล:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างข้อมูล", use_container_width=True):
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

# --- 5. LOGIC (วิเคราะห์ปัจจุบัน + อนาคต) ---
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์และคาดการณ์งานล่วงหน้า..."):
        try:
            prompt = f"""วิเคราะห์ภาพในฐานะ BHOON KHARN AI โหมด: {mode}
            1. [ANALYSIS] สรุปหน้างานปัจจุบันจากรูปภาพ
            2. [RISK] จุดวิกฤตหรือจุดที่เสี่ยงจะผิดพลาดในตอนนี้
            3. [FUTURE] วิเคราะห์งานที่จะเกิดขึ้นถัดไปจากจุดนี้ และสิ่งที่ต้องเตรียมตัวล่วงหน้า
            4. [OWNER_ADVICE] สิ่งที่เจ้าของบ้านต้องรู้เกี่ยวกับงานปัจจุบันและงานต่อเนื่องที่กำลังจะถึง
            5. แนะนำคำถาม 3 ข้อ โดยขึ้นต้นว่า 'ถามช่าง: ' ทุกข้อ"""
            
            inps = [prompt]
            if bp: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            txt = res.text
            
            st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.rep = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            st.session_state.chat = []
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def ask_more(query):
    if st.session_state.engine:
        try:
            res = st.session_state.engine.generate_content(f"ในฐานะ BHOON KHARN AI ตอบคำถาม: {query}")
            st.session_state.chat.append({"role": "user", "content": query})
            st.session_state.chat.append({"role": "assistant", "content": res.text})
        except Exception as e:
            st.error(f"ไม่สามารถตอบคำถามได้: {str(e)}")

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# ใช้ Container เพื่อลดอาการจอกระตุก
report_area = st.container()

if st.session_state.rep:
    with report_area:
        st.divider()
        res = st.session_state.rep
        sections = [
            ("🔍 สรุปการวิเคราะห์หน้างาน", "[ANALYSIS]"),
            ("⏱️ จุดวิกฤตที่ต้องตรวจสอบ", "[RISK]"),
            ("🚀 งานในอนาคตและสิ่งที่ต้องเตรียม", "[FUTURE]"),
            ("🏠 สิ่งที่เจ้าของบ้านต้องทราบ", "[OWNER_ADVICE]")
        ]
        
        for title, tag in sections:
            if tag in res:
                content = res.split(tag)[1].split("[")[0].strip()
                st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)

        if st.session_state.qs:
            st.write("")
            st.markdown("<p style='font-size:0.85rem; font-weight:bold; color:#1E3A8A;'>💡 ถาม BHOON KHARN AI ต่อ:</p>", unsafe_allow_html=True)
            qcols = st.columns(len(st.session_state.qs))
            for i, qv in enumerate(st.session_state.qs):
                if qcols[i].button("🔎 " + qv, key=f"bkq_{i}", use_container_width=True):
                    ask_more(qv)

        # ส่วนของแชทชวนคุยต่อ
        for m in st.session_state.chat:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        st.markdown("<div class='maroon-note'><strong>หมายเหตุ:</strong> การประเมินนี้ทำโดยวิศวกรรม AI จากรูปภาพเบื้องต้นเท่านั้น ไม่สามารถใช้แทนวิศวกรวิชาชีพได้</div>", unsafe_allow_html=True)

# ช่องพิมพ์คำถาม (จะอยู่ล่างสุดเสมอ)
if st.session_state.rep:
    if ui := st.chat_input("สอบถามงานต่อเนื่องหรือจุดที่สงสัย..."):
        ask_more(ui)
        st.rerun()
