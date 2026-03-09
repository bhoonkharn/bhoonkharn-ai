import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. CSS & Style (บีบอัดให้สั้นที่สุด)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    .maroon { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 30px; padding-top: 10px; }
    .owner { border-left: 5px solid #1E3A8A; padding-left: 15px; margin-bottom: 20px; line-height: 1.7; color: #333; }
    div.stButton > button { font-size: 0.7rem !important; height: 24px !important; color: #666 !important; }
    .q-lbl { font-size: 0.7rem; color: #999; margin-top: 15px; }
</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Engine Setup
def get_ks():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for s in st.secrets.keys():
        if "API_KEY" in s.upper() and st.secrets[s] not in k: k.append(st.secrets[s])
    return k

@st.cache_resource
def init_ai(ks):
    if not ks: return None, "No Key"
    random.shuffle(ks)
    for pk in ks:
        try:
            genai.configure(api_key=pk)
            m = genai.GenerativeModel("gemini-1.5-flash-latest")
            m.generate_content("ping")
            return m, "Ready"
        except: continue
    return None, "Error"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai(get_ks())
for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# 3. Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if st.session_state.engine: st.success("🟢 AI Ready")
    else: st.error(f"🔴 {st.session_state.status}")
    if st.button("🔄 Reconnect"): st.session_state.engine = None; st.rerun()
    st.divider()
    mode = st.radio("Mode:", ["📊 เทคนิค", "🏠 เจ้าของบ้าน"])
    if st.button("🗑️ Clear All"):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# 4. Uploaders
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน", type=['jpg','png','jpeg'])
    if bp: st.image(bp, use_container_width=True)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','png','jpeg'])
    if site: st.image(site, use_container_width=True)

def run_q(q):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("BHOON KHARN AI Analysis: " + q)
    st.session_state.chat.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. Analysis
if st.button("🚀 วิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI Not Ready")
    elif site or bp:
        with st.spinner('Analysing...'):
            try:
                p = f"Analyze construction as BHOON KHARN AI. Mode: {mode}\n"
                p += "🔍 วิเคราะห์หน้างาน: (summary)\n⏱️ จุดตายวิกฤต: (risk)\n⚠️ ผลกระทบ: (domino)\n"
                p += "🏗️ มาตรฐาน: (standards)\n🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (list * no HTML)\n"
                p += "Recommend 3 questions with 'ถามช่าง:'"
                inps = [p]
                if bp: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                res = st.session_state.engine.generate_content(inps).text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", res)[:3]]
                st.session_state.rep = re.sub(r"ถามช่าง: .*", "", res, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.rep}]
                st.rerun()
            except Exception as e: st.error(str(e))
    else: st.warning("อัปโหลดรูปก่อนครับ")

# 6. Result Display
if st.session_state.rep:
    st.divider(); st.subheader("📋 ผลวิเคราะห์")
    rt = st.session_state.rep
    hds = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
           ("⚠️ ผลกระทบ", r"⚠️.*?ผลกระทบ"), ("🏗️ มาตรฐาน", r"🏗️.*?มาตรฐาน"),
           ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
    pos = sorted([(re.search(pt, rt).start(), tit, re.search(pt, rt).end()) for tit, pt in hds if re.search(pt, rt)])
    
    if not pos: st.markdown(rt)
    else:
        for i in range(len(pos)):
            s, e = pos[i][2], pos[i+1][0] if i+1 < len(pos) else len(rt)
            title, cont = pos[i][1], rt[s:e].strip().strip(':').strip()
            if "🏠" in title:
                st.markdown(f"#### {title}")
                st.markdown(f"<div class='owner'>{cont}</div>", unsafe_allow_html=True)
            elif "🔍" in title: st.info(cont)
            else:
                with st.expander(f"**{title}**"): st.markdown(cont)

    if st.session_state.qs:
        st.markdown("<p class='q-lbl'>💡 ถาม BHOON KHARN AI ต่อ:</p>", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if cols[i].button("🔎 "+qv, key=f"b_{i}", use_container_width=True): run_q(qv)

    if len(st.session_state.chat) > 1:
        for m in st.session_state.chat[1:]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
    if u_i := st.chat_input("สอบถามเพิ่มเติม..."): run_q(u_i)
    st.markdown("<div class='maroon'><strong>ข้อกำหนด:</strong> ประเมินเบื้องต้นจากรูปเท่านั้น ไม่แทนที่การตรวจโดยวิศวกร</div>", unsafe_allow_html=True)
