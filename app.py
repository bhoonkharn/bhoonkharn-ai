import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. Branding & UI Style
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""
    <style>
    .maroon-note { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 30px; padding-top: 10px; }
    .owner-section { border-left: 5px solid #1E3A8A; padding-left: 20px; margin-bottom: 20px; line-height: 1.8; color: #31333F; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border-radius: 4px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Engine Logic
def get_keys():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for s in st.secrets.keys():
        if "API_KEY" in s.upper() and st.secrets[s] not in k: k.append(st.secrets[s])
    return k

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "No API Key Found"
    random.shuffle(keys)
    for pk in keys:
        try:
            genai.configure(api_key=pk)
            m = genai.GenerativeModel("gemini-1.5-flash-latest")
            m.generate_content("ping")
            return m, "Ready"
        except: continue
    return None, "Connection Failed"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())
for key in ["chat", "report", "qs"]:
    if key not in st.session_state: st.session_state[key] = [] if key != "report" else ""

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
    if bp: st.image(bp, caption="Plan", use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site: st.image(site, caption="Site", use_container_width=True)

def run_q(query):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": query})
    res = st.session_state.engine.generate_content("ในฐานะ BHOON KHARN AI: " + query)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. Analysis Execution
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI Not Ready")
    elif site or bp:
        with st.spinner('Analyzing...'):
            try:
                p = "Analyze construction images as BHOON KHARN AI adviser:\n"
                p += "🔍 วิเคราะห์หน้างาน: (summary)\n⏱️ จุดตายวิกฤต: (risks)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (consequences)\n🏗️ มาตรฐานเทคนิค: (standards)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (list with * no HTML)\n"
                p += "Recommend 3 questions starting with 'ถามช่าง:'. Mode: " + mode
                inputs = [p]
                if bp: inputs.append(Image.open(bp))
                if site: inputs.append(Image.open(site))
                resp = st.session_state.engine.generate_content(inputs).text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", resp)[:3]]
                st.session_state.report = re.sub(r"ถามช่าง: .*", "", resp, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.report}]
                st.rerun()
            except Exception as e: st.error(str(e))
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# 6. Display Area
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
                title, content = pos[i][1], r_txt[s:e].strip().strip(':').strip()
                if "🏠" in title:
                    st.markdown(f"#### {title}")
                    st.markdown(f"<div class='owner-section'>{content}</div>", unsafe_allow_html=True)
                elif "🔍" in title: st.info(content)
                else:
                    with st.expander(f"**{title}**"): st.markdown(content)

        st.download_button("📥 บันทึก", st.session_state.report, "BK_Report.txt")

        if st.session_state.qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อ:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for i, q in enumerate(st.session
