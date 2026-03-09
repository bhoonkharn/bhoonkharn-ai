import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. ตั้งค่าหน้าเว็บและ CSS (เน้นความคลีนและสัดส่วนเล็กตามสั่ง)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""
    <style>
    .maroon-note { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 30px; padding-top: 10px; }
    .owner-box { border-left: 5px solid #1E3A8A; padding-left: 15px; margin-bottom: 20px; line-height: 1.7; color: #333; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border-radius: 4px !important; }
    .subtle-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ Engine (แก้ปัญหา 404 โดยการค้นหารุ่นที่ใช้งานได้อัตโนมัติ)
def get_api_keys():
    keys = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for k in st.secrets.keys():
        if "API_KEY" in k.upper() and st.secrets[k] not in keys: keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "❌ ไม่พบ API Key"
    random.shuffle(keys)
    for pk in keys:
        try:
            genai.configure(api_key=pk)
            # ค้นหาชื่อรุ่นที่ Support การวิเคราะห์ภาพในปัจจุบัน
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0]
            model = genai.GenerativeModel(target)
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "❌ เชื่อมต่อล้มเหลว (Check Secrets)"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_api_keys())
for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# 3. Sidebar (เมนูตั้งค่า)
with st.sidebar:
    st.header("⚙️ Settings")
    if st.session_state.engine: st.success("🟢 AI Online")
    else: st.error(st.session_state.status)
    if st.button("🔄 Reconnect"): 
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน", type=['jpg', 'png', 'jpeg'])
    if bp: st.image(bp, use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site: st.image(site, use_container_width=True)

def run_q(query):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": query})
    res = st.session_state.engine.generate_content("ในฐานะ BHOON KHARN AI: " + query)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. วิเคราะห์ (Logic แบบกระชับกันโค้ดตัด)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI Not Ready")
    elif site or bp:
        with st.spinner('กำลังวิเคราะห์...'):
            try:
                p = f"Analyze as BHOON KHARN AI advisor. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (summary)\n⏱️ จุดตายวิกฤต: (risks)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (consequences)\n🏗️ มาตรฐานเทคนิค: (standards)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (list with * no HTML)\n"
                p += "Recommend 3 short questions starting with 'ถามช่าง:'"
                inps = [p]
                if bp: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                resp = st.session_state.engine.generate_content(inps).text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", resp)[:3]]
                st.session_state.rep = re.sub(r"ถามช่าง: .*", "", resp, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.rep}]
                st.rerun()
            except Exception as e: st.error(str(e))
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# 6. ส่วนการแสดงผล (ล็อกตำแหน่ง Container)
report_area = st.container()
if st.session_state.rep:
    with report_area:
        st.divider(); st.subheader("📋 ผลการตรวจสอบ")
        r_txt = st.session_state.rep
        h_map = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
                 ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"), ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
                 ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        pos = sorted([(re.search(pt, r_txt).start(), tit, re.search(pt, r_txt).end()) for tit, pt in h_map if re.search(pt, r_txt)])
        
        if not pos: st.markdown(r_txt)
        else:
            for i in range(len(pos)):
                s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(r_txt)
                title, cont = pos[i][1], r_txt[s:e].strip().strip(':').strip()
                if "🏠" in title:
                    st.markdown(f"#### {title}")
                    st.markdown(f"<div class='owner-box'>{cont}</div>", unsafe_allow_html=True)
                elif "🔍" in title: st.info(cont)
                else:
                    with st.expander(f"**{title}**"): st.markdown(cont)

        st.download_button("📥 บันทึกรายงาน", st.session_state.rep, "BK_Report.txt")

        if st.session_state.qs:
            st.markdown("<p class='subtle-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for i, qv in enumerate(st.session_state.qs):
                if cols[i].button("🔎 "+qv, key=f"bk_{i}", use_container_width=True): run_q(qv)

    if len(st.session_state.chat) > 1:
        st.divider()
        for m in st.session_state.chat[1:]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
    if u_i := st.chat_input("สอบถามเพิ่มเติม..."): run_query(u_i)

    st.markdown("""<div class="maroon-note"><strong>ข้อกำหนดการใช้งาน:</strong><br>
    • ประเมินเบื้องต้นจากรูปเท่านั้น ไม่แทนที่การตรวจสอบโดยวิศวกรวิชาชีพ โปรดปรึกษาวิศวกรของท่านก่อนดำเนินการ</div>""", unsafe_allow_html=True)
