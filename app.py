import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & PREMIUM BHOON KHARN STYLE ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    
    /* โทนสีจากหน้าเว็บ BHOON KHARN */
    :root {
        --bk-gold: #B59473;
        --bk-dark: #4A3F35;
        --bk-text: #333333;
    }

    html, body, [class*="st-"] { 
        font-family: 'Sarabun', sans-serif; 
        line-height: 1.7; 
        font-size: 0.95rem; /* ขนาดตัวหนังสือเล็กลงให้ดูทางการ */
    }

    /* หัวข้อหลักแบบ Sharp Look */
    .main-title { 
        color: var(--bk-gold); 
        text-align: center; 
        font-weight: 700; 
        font-size: 1.8rem; 
        letter-spacing: 2px;
        margin-bottom: 5px; 
    }
    .brand-sub {
        text-align: center;
        color: var(--bk-dark);
        font-size: 0.75rem;
        letter-spacing: 1px;
        margin-bottom: 40px;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* หัวข้อรายงานแบบมินิมอล */
    .section-header { 
        color: var(--bk-gold); 
        font-size: 1rem; 
        font-weight: 700; 
        margin-top: 25px; 
        margin-bottom: 8px; 
        border-bottom: 1px solid #eee; 
        padding-bottom: 5px; 
        text-transform: uppercase;
    }

    /* เนื้อหาโหมดเจ้าของบ้าน - คลีนและแยกบรรทัดชัดเจน */
    .owner-content { 
        border-left: 3px solid var(--bk-gold); 
        padding-left: 20px; 
        margin: 15px 0; 
        background: transparent !important; 
        color: inherit !important; 
        white-space: pre-line; /* แก้ปัญหาตัวหนังสือติดกัน */
        font-size: 0.95rem;
    }
    
    /* ปุ่มสไตล์มินิมอล (Outline) */
    div.stButton > button { 
        font-size: 0.8rem !important; 
        border-radius: 4px !important; 
        border: 1px solid var(--bk-gold) !important;
        background-color: transparent !important;
        color: var(--bk-gold) !important;
        padding: 5px 20px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: var(--bk-gold) !important;
        color: white !important;
    }

    /* กล่องติดต่อทีมงาน BHOON KHARN */
    .contact-box {
        border-top: 1px solid #eee;
        margin-top: 50px;
        padding: 30px 0;
        text-align: center;
    }
    .contact-title { color: var(--bk-gold); font-weight: 700; font-size: 1rem; margin-bottom: 10px; }
    .contact-info { font-size: 0.9rem; color: var(--bk-dark); }

    /* หมายเหตุแดงเลือดหมูแบบจาง */
    .maroon-note { 
        color: #8B0000; 
        font-size: 0.8rem; 
        margin-top: 20px; 
        text-align: center; 
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE --- (คงเดิมทุกประการ)
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "กรุณาตั้งค่า API Key"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        return model, "Ready"
    except Exception:
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name), "Ready"
        except: pass
        return None, "Connection Error"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. SIDEBAR --- (คงเดิม)
with st.sidebar:
    st.markdown("### BHOON KHARN")
    if "Ready" in st.session_state.status: st.success("Connected")
    else: st.error("Offline")
    mode = st.radio("View Mode:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# --- 4. MAIN UI --- (คงเดิม รองรับ PDF)
st.markdown("<div class='main-title'>BHOON KHARN</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-sub'>Analyze my home with AI</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนก่อสร้าง", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 สภาพหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 5. LOGIC --- (คงเดิม แต่ปรับ Prompt เล็กน้อยให้จัดบรรทัด)
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังวิเคราะห์..."):
        try:
            prompt = f"""วิเคราะห์ภาพในฐานะ BHOON KHARN AI โหมด: {mode} หัวข้อ: 
            [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] (และงานต่อเนื่องในอนาคต)
            เขียนแยกข้อให้ชัดเจน และแนะนำ 3 คำถามสำคัญขึ้นต้นด้วย 'ถามช่าง: ' แยกบรรทัด"""
            inps = [prompt]
            if bp:
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
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
    sections = [
        ("🔍 สรุปผลการวิเคราะห์หน้างาน", "[ANALYSIS]"), 
        ("⏱️ จุดวิกฤตที่ต้องตรวจสอบ", "[RISK]"), 
        ("📝 เทคนิคการตรวจและจุดระบุพิเศษ", "[CHECKLIST]"),
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
        st.markdown("<p style='font-size:0.8rem; font-weight:bold; color:var(--bk-gold);'>💡 ถามต่อ:</p>", unsafe_allow_html=True)
        qcols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if qcols[i].button(qv, key=f"bkq_{i}", use_container_width=True):
                ask_more(qv)

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if ui := st.chat_input("สอบถามเพิ่มเติม..."):
        ask_more(ui)
        st.rerun()

    # CONTACT SECTION (BHOON KHARN BRANDING)
    st.markdown(f"""
    <div class='contact-box'>
        <div class='contact-title'>🛠️ รับคำแนะนำวิธีแก้ไขจากทีม BHOON KHARN (ฟรี)</div>
        <div class='contact-info'>
            📞 โทร: <a href='tel:0887776566' style='color:var(--bk-gold); text-decoration:none;'>088-777-6566</a> | 
            💬 Line ID: <a href='https://line.me/ti/p/~bhoonkharn' style='color:var(--bk-gold); text-decoration:none;'>bhoonkharn</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='maroon-note'>หมายเหตุ: การประเมินนี้ทำโดยวิศวกรรม AI จากรูปภาพเบื้องต้นเท่านั้น ไม่สามารถใช้แทนการตรวจสอบหน้างานจริงได้</div>", unsafe_allow_html=True)
