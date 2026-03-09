import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. Page Config & CSS (เน้นสัดส่วนที่ถูกต้องและสีแดงเลือดหมู)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    .maroon { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 30px; padding-top: 10px; }
    .owner-box { border-left: 5px solid #1E3A8A; padding-left: 15px; margin-bottom: 25px; color: #31333F !important; line-height: 1.8; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #555 !important; border: 1px solid #eee !important; }
    .q-lbl { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Engine Logic (ระบบหมุนเวียน Key และรุ่น AI อัจฉริยะ)
def get_all_keys():
    k_list = []
    if "GOOGLE_API_KEY" in st.secrets: k_list.append(st.secrets["GOOGLE_API_KEY"])
    for key in st.secrets.keys():
        if "API_KEY" in key.upper() and st.secrets[key] not in k_list:
            k_list.append(st.secrets[key])
    return k_list

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "❌ ไม่พบ API Key"
    random.shuffle(keys)
    # ลำดับรุ่นที่เน้น Quota เยอะ (1.5 Flash มี 1,500 requests/day)
    models_to_try = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash"]
    for pk in keys:
        genai.configure(api_key=pk)
        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(m_name)
                model.generate_content("ping")
                return model, f"Online ({m_name})"
            except: continue
    return None, "❌ ทุกรุ่นโควตาเต็ม (โปรดลองเชื่อมต่อใหม่)"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_all_keys())

for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# 3. Sidebar (เมนูตั้งค่า)
with st.sidebar:
    st.header("⚙️ ระบบหลังบ้าน")
    if st.session_state.engine: st.success(f"🟢 {st.session_state.status}")
    else: st.error(st.session_state.status)
    if st.button("🔄 รีเซ็ต/เปลี่ยน Key"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# 4. Uploaders (ประจำตำแหน่งไม่หาย)
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
    res = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN AI: " + q)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. วิเคราะห์ (บีบอัด Prompt กันโค้ดตัด)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                p = f"Analyze as BHOON KHARN AI advisor. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (summary)\n⏱️ จุดตายวิกฤต: (risks)\n⚠️ ผลกระทบ: (domino)\n"
                p += "🏗️ มาตรฐานเทคนิค: (standards)\n🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (ใช้ * และขึ้นบรรทัดใหม่ 2 ครั้งทุกข้อ ห้ามใช้ HTML)\n"
                p += "แนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:'"
                inps = [p]
                if bp: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                resp = st.session_state.engine.generate_content(inps).text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", resp)[:3]]
                st.session_state.rep = re.sub(r"ถามช่าง: .*", "", resp, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.rep}]
                st.rerun()
            except Exception as e: st.error(f"เกิดข้อผิดพลาด: {str(e)}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# 6. Display Area (ล็อกตำแหน่ง Container)
rep_area = st.container()
if st.session_state.rep:
    with rep_area:
        st.divider(); st.subheader("📋 รายงานวิเคราะห์")
        rt = st.session_state.rep
        hds = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
               ("⚠️ ผลกระทบ", r"⚠️.*?ผลกระทบ"), ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
               ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        pos = sorted([(re.search(pt, rt).start(), tit, re.search(pt, rt).end()) for tit, pt in hds if re.search(pt, rt)])
        
        if not pos: st.markdown(rt)
        else:
            for i in range(len(pos)):
                s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(rt)
                title, cont = pos[i][1], rt[s:e].strip().strip(':').strip()
                if "🏠" in title:
                    st.markdown(f"#### {title}")
                    st.markdown(f"<div class='owner-box'>", unsafe_allow_html=True)
                    st.markdown(cont.replace("* ", "\n\n* "))
                    st.markdown("</div>", unsafe_allow_html=True)
                elif "🔍" in title: st.info(cont)
                else:
                    with st.expander(f"**{title}**"): st.markdown(cont)

        if st.session_state.qs:
            st.markdown("<p class='q-lbl'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for i, qv in enumerate(st.session_state.qs):
                if cols[i].button("🔎 "+qv, key=f"bk_{i}", use_container_width=True): run_q(qv)

    if len(st.session_state.chat) > 1:
        st.divider()
        for m in st.session_state.chat[1:]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
    if ui := st.chat_input("สอบถามเพิ่มเติม..."): run_q(ui)
    st.markdown("""<div class='maroon'><strong>ข้อกำหนดการใช้งาน:</strong><br>• ประเมินเบื้องต้นจากรูปเท่านั้น ไม่แทนการตรวจสอบโดยวิศวกรวิชาชีพ โปรดปรึกษาวิศวกรของท่านก่อนดำเนินการ</div>""", unsafe_allow_html=True)
