import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE (ล้างฉากหลังและปรับสีตัวอักษรให้มาตรฐาน 100%) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Sarabun', sans-serif; 
        line-height: 1.8; 
    }
    
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 30px; }
    
    /* หัวข้อ Section */
    .section-header {
        color: #1E3A8A;
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
        border-bottom: 2px solid #eee;
        padding-bottom: 5px;
    }

    /* โหมดเจ้าของบ้าน - ล้างฉากหลัง ใช้สีและฟอนต์มาตรฐานเดียวกับระบบ */
    .owner-content { 
        border-left: 5px solid #1E3A8A; 
        padding-left: 20px; 
        margin: 20px 0;
        background: transparent !important; /* บังคับไม่มีฉากหลัง */
        color: inherit !important; /* ใช้สีเดียวกับข้อความปกติของแอป */
        font-size: 1rem; /* ขนาดเท่ากับข้อความปกติ */
    }
    
    /* ปุ่มคำถามชวนคุย (จิ๋ว 0.7rem) */
    div.stButton > button { 
        font-size: 0.75rem !important; 
        border-radius: 10px !important;
        color: #555 !important;
    }

    /* หมายเหตุสีแดงเลือดหมู */
    .maroon-note { 
        color: #8B0000; 
        font-size: 0.85rem; 
        border-top: 1px solid #eee; 
        margin-top: 40px; 
        padding-top: 20px; 
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (BHOON KHARN AI ONLY) ---
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

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    if "สำเร็จ" in st.session_state.status:
        st.success(st.session_state.status)
    else:
        st.error(st.session_state.status)
        
    if st.button("🔄 เริ่มต้นระบบใหม่", use_container_width=True):
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
    if not st.session_state.engine:
        st.error("ระบบยังไม่พร้อม")
        return

    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            prompt = f"""วิเคราะห์ภาพในฐานะ BHOON KHARN AI โหมด: {mode}
            หัวข้อ:
            [ANALYSIS] สรุปหน้างาน
            [RISK] จุดวิกฤตที่ต้องระวัง
            [STANDARD] มาตรฐานวิศวกรรม
            [OWNER_NOTE] คำแนะนำสำคัญถึงเจ้าของบ้าน
            และคำแนะนำ 3 ข้อ โดยขึ้นต้นว่า 'ถามช่าง: ' ทุกข้อ"""
            
            inps = [prompt]
            if bp: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            txt = res.text
            
            st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.rep = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            st.session_state.chat = [{"role": "assistant", "content": "วิเคราะห์เรียบร้อยครับ"}]
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

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
    
    sections = [
        ("🔍 สรุปการวิเคราะห์หน้างาน", "[ANALYSIS]"),
        ("⏱️ จุดวิกฤตที่ต้องตรวจสอบ", "[RISK]"),
        ("🏗️ มาตรฐานงานช่างและวิศวกรรม", "[STANDARD]"),
        ("🏠 สิ่งที่เจ้าของบ้านต้องทราบ", "[OWNER_NOTE]")
    ]
    
    for title, tag in sections:
        if tag in res:
            content = res.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            
            if tag == "[OWNER_NOTE]":
                # ใช้คลาสใหม่ที่บังคับโปร่งใสและสีมาตรฐาน
                st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else:
                st.write(content)

    # คำถามชวนคุยต่อ
    if st.session_state.qs:
        st.write("")
        st.markdown("<p style='font-size:0.85rem; font-weight:bold; color:#1E3A8A;'>💡 ถาม BHOON KHARN AI ต่อ:</p>", unsafe_allow_html=True)
        qcols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if qcols[i].button("🔎 " + qv, key=f"bkq_{i}", use_container_width=True):
                ask_more(qv)
                st.rerun()

    # Chat
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if ui := st.chat_input("สอบถามเพิ่มเติม..."):
        ask_more(ui)
        st.rerun()

    # หมายเหตุ (แดงเลือดหมู)
    st.markdown("""
    <div class='maroon-note'>
        <strong>หมายเหตุ:</strong> การประเมินนี้ทำโดยวิศวกรรม AI จากรูปภาพเบื้องต้นเท่านั้น ข้อมูลนี้ไม่สามารถนำไปใช้อ้างอิงทางกฎหมาย 
        หรือทดแทนการตรวจสอบหน้างานจริงโดยวิศวกรวิชาชีพได้ กรุณาปรึกษาวิศวกรควบคุมงานของท่านอีกครั้งเพื่อความถูกต้อง
    </div>
    """, unsafe_allow_html=True)
