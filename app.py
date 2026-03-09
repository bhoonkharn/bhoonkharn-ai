import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. Page Config & CSS (เน้นคลีนและสัดส่วนที่ถูกต้อง)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""
    <style>
    .disclaimer { color: #8B0000; font-size: 0.8rem; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
    .owner-box { padding: 5px 0 5px 20px; border-left: 5px solid #1E3A8A; margin-bottom: 25px; color: #31333F; line-height: 1.8; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border-radius: 4px !important; border: 1px solid #eee !important; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Robust Engine (แก้ปัญหา 404 และการเชื่อมต่อ)
def get_keys():
    k = []
    if "GOOGLE_API_KEY" in st.secrets: k.append(st.secrets["GOOGLE_API_KEY"])
    for s_key in st.secrets.keys():
        if "API_KEY" in s_key.upper() and st.secrets[s_key] not in k: k.append(st.secrets[s_key])
    return k

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "❌ ไม่พบ API Key"
    random.shuffle(keys)
    for pk in keys:
        try:
            genai.configure(api_key=pk)
            # ใช้ชื่อรุ่นที่ถูกต้องสำหรับปี 2026
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "❌ การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())

if "chat" not in st.session_state: st.session_state.chat = []
if "report" not in st.session_state: st.session_state.report = ""
if "qs" not in st.session_state: st.session_state.qs = []

# 3. Sidebar (เมนูตั้งค่า)
with st.sidebar:
    st.header("⚙️ ระบบ BHOON KHARN")
    if st.session_state.engine: st.success("🟢 AI พร้อมใช้งาน")
    else: st.error(st.session_state.status)
    if st.button("🔄 เชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.report, st.session_state.qs = [], "", []
        st.rerun()

# 4. Uploaders (ประจำตำแหน่งเดิมไม่หายแน่นอน)
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
    if bp: st.image(bp, caption="Ref", use_container_width=True)
with c2:
    site = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site: st.image(site, caption="Site", use_container_width=True)

def run_q(q_val):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q_val})
    res = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN AI: " + q_val)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                p = "ที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพเริ่มทันที:\n"
                p += "🔍 วิเคราะห์หน้างาน: (ระบุงานและสถานะ)\n"
                p += "⏱️ จุดตายวิกฤต: (ระบุความเสี่ยง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect)\n"
                p += "🏗️ มาตรฐานเทคนิค: (วสท./มยผ.)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (เป็นข้อๆ * นำหน้า ห้ามใช้ HTML)\n"
                p += "ท้ายรายงานแนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:' โหมด: " + mode
                
                inputs = [p]
                if bp: inputs.append(Image.open(bp))
                if site: inputs.append(Image.open(site))
                
                resp = st.session_state.engine.generate_content(inputs)
                txt = resp.text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", txt)[:3]]
                st.session_state.report = re.sub(r"ถามช่าง: .*", "", txt, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.report}]
                st.rerun()
            except Exception as e: st.error(str(e))
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 6. Report Area
rep_area = st.container()
if st.session_state.report:
    with rep_area:
        st.divider()
        st.subheader("📋 ผลการตรวจสอบ")
        r_txt = st.session_state.report
        h_map = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), 
                 ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
                 ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"),
                 ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
                 ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        
        pos = sorted([(re.search(pat, r_txt).start(), tit, re.search(pat, r_txt).end()) 
                      for tit, pat in h_map if re.search(pat, r_txt)])
        
        if not pos: st.markdown(r_txt)
        else:
            for i in range(len(pos)):
                s_c, e_c = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(r_txt)
                title_c, content_c = pos[i][1], r_txt[s_c:e_c].strip().strip(':').strip()
                if "🏠" in title_c:
                    st.markdown("#### " + title_c)
                    st.markdown("<div class='owner-box'>" + content_c + "</div>", unsafe_allow_html=True)
                elif "🔍" in title_c: st.info(content_c)
                else:
                    with st.expander("**" + title_c + "**"): st.markdown(content_c)

        st.download_button("📥 บันทึกรายงาน", st.session_state.report, "BK_Report.txt")

        if st.session_state.qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for
