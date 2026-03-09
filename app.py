import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. Page Config & Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
    <style>
    .disclaimer-text { color: #8B0000; font-size: 0.8rem; margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee; }
    .check-box { padding: 5px 0 5px 20px; border-left: 4px solid #1E3A8A; margin-bottom: 20px; color: #31333F; line-height: 1.7; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border-radius: 4px !important; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Engine & Session States
def get_keys():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for key in st.secrets.keys():
        if "API_KEY" in key.upper() and st.secrets[key] not in k: k.append(st.secrets[key])
    return k

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "No API Key Found"
    random.shuffle(keys)
    for p_key in keys:
        try:
            genai.configure(api_key=p_key)
            m = genai.GenerativeModel("gemini-1.5-flash")
            m.generate_content("ping")
            return m, "Ready"
        except: continue
    return None, "Connection Failed"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "report" not in st.session_state: st.session_state.report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if st.session_state.engine: st.success("🟢 AI Ready")
    else: st.error(f"🔴 {st.session_state.status}")
    if st.button("🔄 Reconnect"): 
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("Report Mode:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.chat_history, st.session_state.report, st.session_state.quick_qs = [], "", []
        st.rerun()

# 4. Upload & Preview
col_l, col_r = st.columns(2)
with col_l:
    blue_print = st.file_uploader("📋 แบบแปลน", type=['jpg', 'png', 'jpeg'])
    if blue_print: st.image(blue_print, caption="Ref", use_container_width=True)
with col_r:
    site_img = st.file_uploader("📸 ภาพหน้างาน", type=['jpg', 'png', 'jpeg'])
    if site_img: st.image(site_img, caption="Site", use_container_width=True)

# 5. Analysis Logic
def run_query(q):
    if not st.session_state.engine: return
    st.session_state.chat_history.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("Analyze as BHOON KHARN AI: " + q)
    st.session_state.chat_history.append({"role": "assistant", "content": res.text})
    st.rerun()

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI Not Ready")
    elif site_img or blue_print:
        with st.spinner('BHOON KHARN AI Analyzing...'):
            try:
                p = "คุณคือที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพนี้เริ่มทันที:\n"
                p += "🔍 วิเคราะห์หน้างาน: (ระบุงานและสถานะ)\n"
                p += "⏱️ จุดตายวิกฤต: (ระบุความเสี่ยงแฝง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect และงบซ่อม)\n"
                p += "🏗️ มาตรฐานเทคนิค: (วสท./มยผ./สากล)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (สรุปเป็นข้อๆ ใช้ * นำหน้า ห้ามใช้ HTML ห้ามใช้ <br/>)\n"
                p += "ท้ายรายงานแนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:' โหมด: " + mode
                
                inputs = [p]
                if blue_print: inputs.append(Image.open(blue_print))
                if site_img: inputs.append(Image.open(site_img))
                
                resp = st.session_state.engine.generate_content(inputs)
                txt = resp.text
                st.session_state.quick_qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", txt)[:3]]
                st.session_state.report = re.sub(r"ถามช่าง: .*", "", txt, flags=re.DOTALL).strip()
                st.session_state.chat_history = [{"role": "assistant", "content": st.session_state.report}]
                st.rerun()
            except Exception as e: st.error(str(e))
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 6. Display Report
report_area = st.container()
if st.session_state.report:
    with report_area:
        st.divider()
        st.subheader("📋 รายงานวิเคราะห์โดย BHOON KHARN AI")
        r_txt = st.session_state.report
        heads = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), 
                 ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
                 ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"),
                 ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
                 ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        
        pos = sorted([(re.search(pat, r_txt).start(), title, re.search(pat, r_txt).end()) 
                      for title, pat in heads if re.search(pat, r_txt)])
        
        if not pos: st.markdown(r_txt)
        else:
            for i in range(len(pos)):
                s = pos[i][2]
                e = pos[i+1][0] if i+1 < len(pos) else len(r_txt)
                content = r_txt[s:e].strip().strip(':').strip()
                if "🏠" in pos[i][1]:
                    st.markdown(f"#### {pos[i][1]}")
                    st.markdown(f"<div class='check-box'>{content}</div>", unsafe_allow_html=True)
                elif "🔍" in pos[i][1]: st.info(content)
                else:
                    with st.expander(f"**{pos[i][1]}**"): st.markdown(content)

        st.download_button("📥 บันทึกรายงาน", st.session_state.report, "BK_Report.txt")

        if st.session_state.quick_qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state
