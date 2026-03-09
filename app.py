import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. Page Config & CSS
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""
    <style>
    .disclaimer { color: #8B0000; font-size: 0.8rem; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
    .owner-box { padding: 5px 0 5px 20px; border-left: 4px solid #1E3A8A; margin-bottom: 20px; color: #31333F; line-height: 1.7; }
    div.stButton > button { font-size: 0.7rem !important; height: 24px !important; color: #666 !important; border-radius: 4px !important; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Engine & States
def get_keys():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for key in st.secrets.keys():
        if "API_KEY" in key.upper() and st.secrets[key] not in k: k.append(st.secrets[key])
    return k

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "No Key"
    random.shuffle(keys)
    for pk in keys:
        try:
            genai.configure(api_key=pk)
            m = genai.GenerativeModel("gemini-1.5-flash")
            m.generate_content("ping")
            return m, "Ready"
        except: continue
    return None, "Failed"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())
if "chat" not in st.session_state: st.session_state.chat = []
if "report" not in st.session_state: st.session_state.report = ""
if "qs" not in st.session_state: st.session_state.qs = []

# 3. Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if st.session_state.engine: st.success("🟢 Ready")
    else: st.error(f"🔴 {st.session_state.status}")
    if st.button("🔄 Reconnect"): 
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("Mode:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.chat, st.session_state.report, st.session_state.qs = [], "", []
        st.rerun()

# 4. Uploaders
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน", type=['jpg', 'png', 'jpeg'])
    if bp: st.image(bp, caption="Ref", use_container_width=True)
with c2:
    site = st.file_uploader("📸 ภาพหน้างาน", type=['jpg', 'png', 'jpeg'])
    if site: st.image(site, caption="Site", use_container_width=True)

def run_q(q):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("Analyze as BHOON KHARN AI: " + q)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. Analyze
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI Not Ready")
    elif site or bp:
        with st.spinner('Analyzing...'):
            try:
                p = "ที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพเริ่มทันที:\n"
                p += "🔍 วิเคราะห์หน้างาน: (สถานะ)\n⏱️ จุดตายวิกฤต: (ความเสี่ยง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect)\n🏗️ มาตรฐานเทคนิค: (วสท.)\n"
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
    else: st.warning("อัปโหลดรูปก่อนครับ")

# 6. Report Area
rep_area = st.container()
if st.session_state.report:
    with rep_area:
        st.divider()
        st.subheader("📋 รายงานวิเคราะห์")
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
                s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(r_txt)
                content = r_txt[s:e].strip().strip(':').strip()
                if "🏠" in pos[i][1]:
                    st.markdown(f"#### {pos[i][1]}")
                    st.markdown(f"<div class='owner-box'>{content}</div>", unsafe_allow_html=True)
                elif "🔍" in pos[i][1]: st.info(content)
                else:
                    with st.expander(f"**{pos[i][1]}**"): st.markdown(content)

        st.download_button("📥 บันทึก", st.session_state.report, "BK_Report.txt")

        if st.session_state.qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for idx, q_val in enumerate(st.session_state.qs):
                if cols[idx].button("🔎 " + q_val, key=f"bk_{idx}", use_container_width=True): run_q(q_val)

    if len(st.session_state.chat) > 1:
        st.divider()
        for msg in st.session_state.chat[1:]:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if u_in := st.chat_input("สอบถามเพิ่มเติม..."): run_q(u_in)

    st.markdown("""<div class="disclaimer"><strong>ข้อกำหนดการใช้งาน:</strong><br>
    • ประเมินเบื้องต้นจากรูปถ่ายเท่านั้น ข้อมูลอาจไม่ครบถ้วนและไม่สามารถใช้แทนการตรวจสอบโดยวิศวกรวิชาชีพได้<br>
    • ความแม่นยำขึ้นอยู่กับความคมชัดของภาพ โปรดปรึกษาวิศวกรควบคุมงานของท่านก่อนดำเนินการใดๆ</div>""", unsafe_allow_html=True)
