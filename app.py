import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# --- 1. SETTING & CSS (UI ที่พี่ต้องการ) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
    <style>
    /* จุดสังเกตเจ้าของบ้าน: เส้นน้ำเงินด้านซ้าย คลีนๆ ไม่จ้าตา */
    .owner-box { 
        border-left: 5px solid #1E3A8A; 
        padding-left: 20px; 
        margin-bottom: 25px; 
        color: #31333F !important; 
        line-height: 1.8; 
    }
    /* หัวข้อและปุ่มถามต่อ: เล็กจิ๋วและสะอาดตา */
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    div.stButton > button { 
        font-size: 0.7rem !important; 
        height: 26px !important; 
        padding: 0px 10px !important;
        color: #666 !important; 
        border: 1px solid #eee !important;
    }
    /* หมายเหตุท้ายรายงาน: สีแดงเลือดหมู */
    .maroon-note { 
        color: #8B0000; 
        font-size: 0.8rem; 
        border-top: 1px solid #eee; 
        margin-top: 40px; 
        padding-top: 10px; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# --- 2. ENGINE LOGIC (ระบบหมุนเวียน Key และกัน Quota เต็ม) ---
def get_all_keys():
    keys = []
    if "GOOGLE_API_KEY" in st.secrets: keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "API_KEY" in k.upper() and st.secrets[k] not in keys: keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "❌ ไม่พบ API Key"
    shuffled_keys = random.sample(keys, len(keys))
    # บังคับใช้รุ่น 1.5 Flash เป็นหลักเพราะโควตาเยอะกว่ารุ่น 2.x ถึง 75 เท่า
    models_to_try = ["gemini-1.5-flash-latest", "gemini-1.5-flash"]
    
    for pk in shuffled_keys:
        genai.configure(api_key=pk)
        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(m_name)
                model.generate_content("ping")
                return model, f"Online ({m_name})"
            except: continue
    return None, "❌ โควตาเต็มทุก Key (โปรดรอ 60 วินาที)"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_all_keys())

for k in ["chat", "report", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "report" else ""

# --- 3. SIDEBAR & UPLOADER (ตำแหน่งคงที่ตลอดเวลา) ---
with st.sidebar:
    st.header("⚙️ ระบบหลังบ้าน")
    if st.session_state.engine: st.success(f"🟢 {st.session_state.status}")
    else: st.error(st.session_state.status)
    if st.button("🔄 ลองเชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.report, st.session_state.qs = [], "", []
        st.rerun()

col1, col2 = st.columns(2)
with col1:
    bp = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg','png','jpeg'])
    if bp: st.image(bp, use_container_width=True)
with col2:
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg','png','jpeg'])
    if site: st.image(site, use_container_width=True)

def run_q(query_text):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": query_text})
    res = st.session_state.engine.generate_content("BHOON KHARN AI: " + query_text)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# --- 4. ANALYSIS EXECUTION ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('BHOON KHARN AI กำลังตรวจสอบ...'):
            try:
                p = f"Analyze as BHOON KHARN AI advisor. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (สรุปสั้น)\n⏱️ จุดตายวิกฤต: (ความเสี่ยง)\n"
                p += "🏗️ มาตรฐานเทคนิค: (วสท./มยผ.)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (เป็นข้อๆ * นำหน้า เว้นบรรทัดใหม่ 2 ครั้งทุกข้อ ห้ามใช้ HTML)\n"
                p += "ท้ายรายงานแนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:'"
                
                inps = [p]
                if bp: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                
                resp = st.session_state.engine.generate_content(inps).text
                # แยกคำถามและเนื้อหา
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", resp)[:3]]
                st.session_state.report = re.sub(r"ถามช่าง: .*", "", resp, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.report}]
                st.rerun()
            except Exception as e: st.error(f"ระบบไม่ว่าง (Quota): {str(e)[:50]}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. RESULT DISPLAY (กันหน้าจอเด้งด้วย Container) ---
res_container = st.container()
if st.session_state.report:
    with res_container:
        st.divider(); st.subheader("📋 รายงานการตรวจสอบ")
        rt = st.session_state.report
        hds = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), 
               ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
               ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
               ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        
        pos = sorted([(re.search(pt, rt).start(), tit, re.search(pt, rt).end()) for tit, pt in hds if re.search(pt, rt)])
        
        if not pos: st.markdown(rt)
        else:
            for i in range(len(pos)):
                s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(rt)
                title, cont = pos[i][1], rt[s:e].strip().strip(':').strip()
                if "🏠" in title:
                    st.markdown(f"#### {title}")
                    st.markdown("<div class='owner-box'>", unsafe_allow_html=True)
                    st.markdown(cont.replace("* ", "\n\n* "))
                    st.markdown("</div>", unsafe_allow_html=True)
                elif "🔍" in title: st.info(cont)
                else:
                    with st.expander(f"**{title}**"): st.markdown(cont)

        # ส่วนถามต่อ (Small UI)
        if st.session_state.qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for i, qv in enumerate(st.session_state.qs):
                if cols[i].button("🔎 "+qv, key=f"bk_{i}", use_container_width=True): run_q(qv)

    if len(st.session_state.chat) > 1:
        st.divider()
        for m in st.session_state.chat[1:]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if u_i := st.chat_input("สอบถามเพิ่มเติม..."): run_q(u_i)
    
    st.markdown("""<div class='maroon-note'><strong>ข้อกำหนดการใช้งาน:</strong><br>
    • ประเมินเบื้องต้นจากรูปถ่ายเท่านั้น ไม่แทนการตรวจสอบโดยวิศวกรวิชาชีพ โปรดปรึกษาวิศวกรของท่านก่อนดำเนินการ</div>""", unsafe_allow_html=True)
