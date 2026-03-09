import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. Branding & UI Style
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""
    <style>
    .maroon-disclaimer { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 30px; padding-top: 10px; }
    .owner-section { border-left: 5px solid #1E3A8A; padding-left: 15px; margin-bottom: 20px; color: #333; line-height: 1.8; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border: 1px solid #eee !important; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Engine Logic (แก้ไขปัญหา 404 และการเชื่อมต่อ)
def get_api_keys():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for s in st.secrets.keys():
        if "API_KEY" in s.upper() and st.secrets[s] not in k: k.append(st.secrets[s])
    return k

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "❌ ไม่พบ API Key"
    random.shuffle(keys)
    for pk in keys:
        try:
            genai.configure(api_key=pk)
            # ลองใช้ชื่อรุ่นแบบมาตรฐานที่สุด
            model = genai.GenerativeModel("gemini-1.5-flash")
            model.generate_content("ping")
            return model, "Ready"
        except:
            try:
                # ถ้าพลาด ลองชื่อรุ่นแบบมี Prefix
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                model.generate_content("ping")
                return model, "Ready"
            except: continue
    return None, "❌ การเชื่อมต่อล้มเหลว (Check Secrets)"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_api_keys())
for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# 3. Sidebar เมนูตั้งค่า
with st.sidebar:
    st.header("⚙️ ระบบหลังบ้าน")
    if st.session_state.engine: st.success("🟢 AI ออนไลน์")
    else: st.error(st.session_state.status)
    if st.button("🔄 ลองเชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูล", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน", type=['jpg','png','jpeg'])
    if bp: st.image(bp, use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg','png','jpeg'])
    if site: st.image(site, use_container_width=True)

def run_q(q):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("Analyze as BHOON KHARN AI: " + q)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มวิเคราะห์ (ตำแหน่งคงที่)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                p = f"Analyze as BHOON KHARN AI advisor. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (สรุปสั้น)\n⏱️ จุดตายวิกฤต: (ความเสี่ยง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect)\n🏗️ มาตรฐานเทคนิค: (มาตรฐาน)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (เป็นข้อๆ * นำหน้า ห้ามใช้ HTML)\n"
                p += "แนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:'"
                inps = [p]
                if bp: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                resp = st.session_state.engine.generate_content(inps).text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", resp)[:3]]
                st.session_state.rep = re.sub(r"ถามช่าง: .*", "", resp, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.rep}]
                st.rerun()
            except Exception as e: st.error(str(e))
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 6. รายงานผล
if st.session_state.rep:
    st.divider(); st.subheader("📋 ผลการตรวจสอบ")
    rt = st.session_state.rep
    hds = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
           ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"), ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
           ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
    pos = sorted([(re.search(pt, rt).start(), tit, re.search(pt, rt).end()) for tit, pt in hds if re.search(pt, rt)])
    
    if not pos: st.markdown(rt)
    else:
        for i in range(len(pos)):
            s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(rt)
            title, cont = pos[i][1], rt[s:e].strip().strip(':').strip()
            if "🏠" in title:
                st.markdown(f"#### {title}")
                st.markdown(f"<div class='owner-section'>{cont}</div>", unsafe_allow_html=True)
            elif "🔍" in title: st.info(cont)
            else:
                with st.expander(f"**{title}**"): st.markdown(cont)

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

    st.markdown("""<div class='maroon-disclaimer'><strong>ข้อกำหนดการใช้งาน:</strong><br>
    • ประเมินเบื้องต้นจากรูปเท่านั้น ไม่แทนที่การตรวจสอบหน้างานจริงโดยวิศวกรวิชาชีพ โปรดปรึกษาวิศวกรของท่านก่อนดำเนินการใดๆ</div>""", unsafe_allow_html=True)
