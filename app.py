import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE --- (แก้ไขแค่จุดเดียวให้รองรับการเว้นบรรทัด)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.8; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 30px; }
    .section-header { color: #1E3A8A; font-size: 1.2rem; font-weight: 700; margin-top: 25px; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    
    /* แก้ไขเฉพาะจุดนี้: เพิ่ม white-space: pre-line เพื่อให้ตัวหนังสือไม่ติดกัน */
    .owner-content { 
        border-left: 5px solid #1E3A8A; 
        padding-left: 20px; 
        margin: 20px 0; 
        background: transparent !important; 
        color: inherit !important; 
        font-size: 1rem;
        white-space: pre-line; 
    }
    
    div.stButton > button { font-size: 0.75rem !important; border-radius: 10px !important; color: #555 !important; }
    .maroon-note { color: #8B0000; font-size: 0.85rem; border-top: 1px solid #eee; margin-top: 40px; padding-top: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE --- (คงเดิมตามพี่ส่งมา)
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "กรุณาตั้งค่า API Key"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        return model, "เชื่อมต่อสำเร็จ"
    except Exception:
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name), "เชื่อมต่อสำเร็จ"
        except: pass
        return None, "การเชื่อมต่อขัดข้อง"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. SIDEBAR --- (คงเดิม)
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    if "สำเร็จ" in st.session_state.status: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    if st.button("🔄 เริ่มต้นระบบใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("มุมมองการแสดงผล:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติงานตรวจ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# --- 4. MAIN UI --- (คงเดิม)
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนก่อสร้าง", type=['jpg','jpeg','png','pdf'])
    if bp:
        if bp.type == "application/pdf": st.info("📂 รับไฟล์แปลน PDF เรียบร้อย")
        else: st.image(bp)
with c2:
    site = st.file_uploader("📸 สภาพหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 5. LOGIC --- (แก้ไขเฉพาะ Prompt ให้ AI เว้นบรรทัด)
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            # เพิ่มคำสั่งให้ AI เขียนแยกข้อและเคาะบรรทัดในส่วน OWNER_NOTE
            prompt = f"""วิเคราะห์ข้อมูลในฐานะ BHOON KHARN AI โหมด: {mode} 
            หัวข้อ: 
            [ANALYSIS] สรุปการวิเคราะห์หน้างานปัจจุบัน
            [RISK] จุดวิกฤตหรือสิ่งที่ต้องระวังเป็นพิเศษ
            [CHECKLIST] เทคนิคการตรวจและจุดที่ต้องตรวจสอบอย่างยิ่ง (ระบุข้อควรรู้และเกณฑ์มาตรฐาน)
            [STANDARD] มาตรฐานงานช่างและวิศวกรรม
            [OWNER_NOTE] คำแนะนำสำคัญถึงเจ้าของบ้านและสิ่งที่ควรรู้เกี่ยวกับงานขั้นตอนถัดไป (กรุณาเขียนแยกเป็นข้อๆ และเว้นบรรทัดระหว่างข้อให้ชัดเจน)
            ถามช่าง: 3 ข้อคำถามแนะนำ"""
            
            inps = [prompt]
            if bp:
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            txt = res.text
            
            st.session_state.qs = [q.strip() for q in re.findall(r"(?:ถามช่าง|คำถามแนะนำ):\s*(.*)", txt)[:3]]
            st.session_state.rep = re.sub(r"(?:ถามช่าง|คำถามแนะนำ):.*", "", txt, flags=re.DOTALL).strip()
            st.session_state.chat = []
        except Exception as e: st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def ask_more(query):
    if st.session_state.engine:
        res = st.session_state.engine.generate_content(f"BHOON KHARN AI: {query}")
        st.session_state.chat.append({"role": "user", "content": query})
        st.session_state.chat.append({"role": "assistant", "content": res.text})

# --- 6. DISPLAY --- (คงเดิม)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพหรือไฟล์แปลน")

if st.session_state.rep:
    st.divider()
    res = st.session_state.rep
    sections = [
        ("🔍 สรุปการวิเคราะห์หน้างาน", "[ANALYSIS]"), 
        ("⏱️ จุดวิกฤตที่ต้องตรวจสอบ", "[RISK]"), 
        ("📝 เทคนิคการตรวจและจุดที่ต้องระบุพิเศษ", "[CHECKLIST]"),
        ("🏗️ มาตรฐานงานช่างและวิศวกรรม", "[STANDARD]"), 
        ("🏠 สิ่งที่เจ้าของบ้านต้องทราบและงานอนาคต", "[OWNER_NOTE]")
    ]
    
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

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if ui := st.chat_input("สอบถามเพิ่มเติม..."):
        ask_more(ui)
        st.rerun()

    st.markdown("<div class='maroon-note'><strong>หมายเหตุ:</strong> ข้อมูลนี้ไม่สามารถนำไปใช้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
