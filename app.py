import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. Branding & UI Style (เน้นความคลีนและขนาดตัวหนังสือที่ถูกต้อง)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""
    <style>
    .maroon-note { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 30px; padding-top: 10px; }
    .owner-section { 
        border-left: 5px solid #1E3A8A; 
        padding-left: 20px; 
        margin-bottom: 25px; 
        color: #31333F !important; 
        line-height: 1.8; 
    }
    /* ปรับปุ่มและหัวข้อถามต่อให้จิ๋วและได้สัดส่วน */
    div.stButton > button { 
        font-size: 0.7rem !important; 
        height: 26px !important; 
        padding: 0px 10px !important;
        color: #555 !important; 
        border-radius: 4px !important; 
    }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Engine Logic (ระบบเชื่อมต่อแบบ Auto-Discovery)
def get_keys():
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
            # ค้นหา Model ที่รองรับการวิเคราะห์ภาพในปัจจุบัน
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0]
            model = genai.GenerativeModel(target)
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "❌ การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())
for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# 3. Sidebar (เมนูตั้งค่า)
with st.sidebar:
    st.header("⚙️ ระบบ BHOON KHARN")
    if st.session_state.engine: st.success("🟢 AI พร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.status}")
    if st.button("🔄 เชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ (ประจำตำแหน่ง)
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน", type=['jpg','png','jpeg'])
    if bp: st.image(bp, use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg','png','jpeg'])
    if site: st.image(site, use_container_width=True)

def run_q(query):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": query})
    res = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN AI: " + query)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('กำลังวิเคราะห์...'):
            try:
                p = f"Analyze as BHOON KHARN AI adviser. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (สรุปสั้น)\n⏱️ จุดตายวิกฤต: (ความเสี่ยง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect)\n🏗️ มาตรฐานเทคนิค: (มาตรฐาน)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (สรุปเป็นข้อๆ โดยใช้ * และเว้น 2 บรรทัดทุกข้อ ห้ามใช้ HTML)\n"
                p += "ท้ายรายงานแนะนำ 3 คำถามสั้นๆ ขึ้นต้นด้วย 'ถามช่าง:'"
                inps = [p]
                if bp: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                resp = st.session_state.engine.generate_content(inps).text
                # จัดการแยกส่วนคำถามและเนื้อหา
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", resp)[:3]]
                st.session_state.rep = re.sub(r"ถามช่าง: .*", "", resp, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.rep}]
                st.rerun()
            except Exception as e: st.error(str(e))
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# 6. ส่วนการแสดงผล (ใช้ Container ป้องกันหน้าจอเด้ง)
rep_area = st.container()
if st.session_state.rep:
    with rep_area:
        st.divider(); st.subheader("📋 ผลการตรวจสอบ")
        r_txt = st.session_state.rep
        h_map = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), 
                 ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
                 ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"), 
                 ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
                 ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        
        pos = sorted([(re.search(pt, r_txt).start(), tit, re.search(pt, r_txt).end()) 
                      for tit, pt in h_map if re.search(pt, r_txt)])
        
        if not pos: st.markdown(r_txt)
        else:
            for i in range(len(pos)):
                s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(r_txt)
                title, cont = pos[i][1], r_txt[s:e].strip().strip(':').strip()
                if "🏠" in title:
                    st.markdown(f"#### {title}")
                    # บังคับการเว้นบรรทัดและสีตัวอักษร
                    clean_cont = cont.replace("* ", "\n\n* ")
                    st.markdown(f"<div class='owner-section'>", unsafe_allow_html=True)
                    st.markdown(clean_cont)
                    st.markdown("</div>", unsafe_allow_html=True)
                elif "🔍" in title: st.info(cont)
                else:
                    with st.expander(f"**{title}**"): st.markdown(cont)

        st.download_button("📥 บันทึกรายงาน", st.session_state.rep, "BK_Report.txt")

        # ส่วนถามต่อ (Small UI)
        if st.session_state.qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for i, qv in enumerate(st.session_state.qs):
                if cols[i].button("🔎 "+qv, key=f"bk_btn_{i}", use_container_width=True): run_q(qv)

    if len(st.session_state.chat) > 1:
        st.divider()
        for m in st.session_state.chat[1:]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
    if u_i := st.chat_input("สอบถามเพิ่มเติม..."): run_query(u_i)

    st.markdown("""<div class='maroon-note'><strong>ข้อกำหนดการใช้งาน:</strong><br>
    • ประเมินเบื้องต้นจากรูปเท่านั้น ไม่แทนที่การตรวจสอบหน้างานจริงโดยวิศวกรวิชาชีพ โปรดปรึกษาวิศวกรของท่านก่อนดำเนินการใดๆ</div>""", unsafe_allow_html=True)
