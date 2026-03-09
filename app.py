import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. UI Setup (เป๊ะตามสเปก: ปุ่มจิ๋ว, เส้นน้ำเงิน, หมายเหตุแดงเลือดหมู)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    /* ส่วนเจ้าของบ้าน: เส้นน้ำเงิน ไม่จ้าตา */
    .owner-box { 
        border-left: 5px solid #1E3A8A; 
        padding: 5px 0 5px 20px; 
        margin-bottom: 25px; 
        color: #31333F !important; 
        line-height: 1.8; 
    }
    /* ปุ่มถามต่อ: เล็กจิ๋วและสะอาดตา */
    div.stButton > button { 
        font-size: 0.7rem !important; 
        height: 26px !important; 
        padding: 0 10px !important; 
        color: #666 !important; 
    }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    /* หมายเหตุ: สีแดงเลือดหมู */
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

# 2. Engine (ระบบหมุนเวียน Key และรุ่น AI เพื่อแก้ Quota)
def get_keys():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for s in st.secrets.keys():
        if "API_KEY" in s.upper() and st.secrets[s] not in k: k.append(st.secrets[s])
    return k

@st.cache_resource
def init_ai(keys):
    if not keys: return None, "ไม่พบ API Key"
    random.shuffle(keys)
    # ลำดับรุ่นที่เน้น 1.5 Flash เป็นหลักเพื่อโควตาที่เสถียร
    models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash"]
    for pk in keys:
        genai.configure(api_key=pk)
        for m_name in models:
            try:
                m = genai.GenerativeModel(m_name)
                m.generate_content("ping")
                return m, f"Online ({m_name})"
            except: continue
    return None, "โควตาเต็มทุก Key (โปรดรอสักครู่)"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai(get_keys())

for k in ["chat", "report", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "report" else ""

# 3. Sidebar (ตำแหน่งคงที่)
with st.sidebar:
    st.header("⚙️ ระบบหลังบ้าน")
    if st.session_state.engine: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    if st.button("🔄 รีเซ็ตการเชื่อมต่อ"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.report, st.session_state.qs = [], "", []
        st.rerun()

# 4. Uploaders
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg','png','jpeg'])
    if bp: st.image(bp, use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg','png','jpeg'])
    if site: st.image(site, use_container_width=True)

def run_q(q):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("BHOON KHARN AI Analysis: " + q)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. Analysis Logic
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('กำลังวิเคราะห์...'):
            try:
                p = f"Analyze as BHOON KHARN AI adviser. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (summary)\n⏱️ จุดตายวิกฤต: (risk)\n"
                p += "🏗️ มาตรฐานเทคนิค: (standards)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (list with * no HTML)\n"
                p += "Recommend 3 questions with 'ถามช่าง:'"
                
                inputs = [p]
                if bp: inputs.append(Image.open(bp))
                if site: inputs.append(Image.open(site))
                
                resp = st.session_state.engine.generate_content(inputs).text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", resp)[:3]]
                st.session_state.report = re.sub(r"ถามช่าง: .*", "", resp, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.report}]
                st.rerun()
            except Exception as e: st.error(f"Error: {str(e)[:100]}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# 6. Result Display (Steady Layout)
out_area = st.container()
if st.session_state.report:
    with out_area:
        st.divider(); st.subheader("📋 ผลการตรวจสอบ")
        rt = st.session_state.report
        hds = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), 
               ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
               ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
               ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        
        pos = sorted([(re.search(pt, rt).start(), tit, re.search(pt, rt).end()) 
                      for tit, pt in hds if re.search(pt, rt)])
        
        if not pos: st.markdown(rt)
        else:
            for i in range(len(pos)):
                s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(rt)
                tit, cont = pos[i][1], rt[s:e].strip().strip(':').strip()
                if "🏠" in tit:
                    st.markdown(f"#### {tit}")
                    st.markdown(f"<div class='owner-box'>", unsafe_allow_html=True)
                    st.markdown(cont.replace("* ", "\n\n* "))
                    st.markdown("</div>", unsafe_allow_html=True)
                elif "🔍" in tit: st.info(cont)
                else:
                    with st.expander(f"**{tit}**"): st.markdown(cont)

        # ถามต่อ (Small UI)
        if st.session_state.qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for i, qv in enumerate(st.session_state.qs):
                if cols[i].button("🔎 "+qv, key=f"bk_{i}", use_container_width=True): run_q(qv)

    if len(st.session_state.chat) > 1:
        st.divider()
        for m in st.session_state.chat[1:]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if ui := st.chat_input("สอบถามเพิ่มเติม..."): run_q(ui)
    
    st.markdown("<div class='maroon-note'><strong>ข้อกำหนดการใช้งาน:</strong><br>• ประเมินเบื้องต้นจากรูปเท่านั้น ไม่แทนการตรวจสอบโดยวิศวกรวิชาชีพ โปรดปรึกษาวิศวกรของท่านก่อนดำเนินการ</div>", unsafe_allow_html=True)
