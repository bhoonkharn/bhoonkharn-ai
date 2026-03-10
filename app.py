import streamlit as st
import google.generativeai as genai
from PIL import Image
import random, re

# 1. CSS & Style
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    .owner { border-left: 5px solid #1E3A8A; padding: 15px; background: #f8f9fa; border-radius: 0 5px 5px 0; margin-bottom: 20px; }
    .q-lbl { font-size: 0.8rem; font-weight: bold; color: #1E3A8A; margin-top: 15px; }
    div.stButton > button { font-size: 0.75rem !important; border-radius: 20px !important; }
    .maroon { color: #8B0000; font-size: 0.8rem; border-top: 1px solid #eee; margin-top: 30px; padding-top: 10px; text-align: center; }
</style>""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h2>", unsafe_allow_html=True)

# 2. Engine Logic
def get_ks():
    k = [st.secrets["GOOGLE_API_KEY"]] if "GOOGLE_API_KEY" in st.secrets else []
    for s in st.secrets.keys():
        if "API_KEY" in s.upper() and st.secrets[s] not in k: k.append(st.secrets[s])
    return k

@st.cache_resource
def init_ai(ks):
    if not ks: return None, "No API Key"
    random.shuffle(ks)
    for pk in ks:
        try:
            genai.configure(api_key=pk)
            # ใช้รุ่นที่เสถียรที่สุดก่อน
            m = genai.GenerativeModel("gemini-1.5-flash")
            m.generate_content("ping")
            return m, "System Ready"
        except: continue
    return None, "Quota Full or Connection Error"

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# 3. Sidebar
with st.sidebar:
    st.header("⚙️ Control Panel")
    m_obj, status = init_ai(get_ks())
    if m_obj: st.success(status)
    else: st.error(status)
    
    mode = st.radio("โหมดการวิเคราะห์:", ["📊 ช่างเทคนิค/วิศวกร", "🏠 เจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# 4. Uploaders
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แนบแปลน (Blueprint)", type=['jpg','png','jpeg'])
    if bp: st.image(bp, caption="แปลนก่อสร้าง")
with c2:
    site = st.file_uploader("📸 รูปหน้างานจริง", type=['jpg','png','jpeg'])
    if site: st.image(site, caption="สภาพหน้างาน")

# 5. Functions
def run_q(q):
    if not m_obj: return
    with st.spinner('AI กำลังตอบ...'):
        res = m_obj.generate_content(f"ในฐานะ BHOON KHARN AI ตอบคำถามนี้: {q}")
        st.session_state.chat.append({"role": "user", "content": q})
        st.session_state.chat.append({"role": "assistant", "content": res.text})

# 6. Analysis Execution
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if not m_obj: 
        st.error("AI ไม่พร้อมใช้งาน")
    elif not (site or bp):
        st.warning("กรุณาอัปโหลดรูปแปลนหรือรูปหน้างานอย่างน้อย 1 รูป")
    else:
        with st.spinner('กำลังประมวลผลภาพและข้อมูลวิศวกรรม...'):
            try:
                prompt = f"""วิเคราะห์ในฐานะ BHOON KHARN AI (เชี่ยวชาญการตรวจงานก่อสร้าง) 
                โหมดผู้ใช้งาน: {mode}
                กรุณาตอบตามโครงสร้างนี้เท่านั้น:
                🔍 วิเคราะห์หน้างาน: (สรุปสิ่งที่เห็นจากภาพ)
                ⏱️ จุดตายวิกฤต: (จุดที่ต้องแก้ไขทันทีหรือห้ามพลาด)
                🏗️ มาตรฐาน: (อ้างอิงมาตรฐานวิศวกรรมที่เกี่ยวข้อง)
                🏠 จุดสังเกตสำหรับเจ้าของบ้าน: (สิ่งที่เจ้าของบ้านต้องคุยกับผู้รับเหมา)
                คำถามแนะนำ (เริ่มด้วย 'ถามช่าง: ' เสมอ 3 ข้อ)"""
                
                content_payload = [prompt]
                if bp: content_payload.append(Image.open(bp))
                if site: content_payload.append(Image.open(site))
                
                response = m_obj.generate_content(content_payload).text
                
                # Parsing Results
                st.session_state.qs = [q.replace("ถามช่าง:", "").strip() for q in re.findall(r"ถามช่าง:.*", response)]
                st.session_state.rep = re.sub(r"ถามช่าง:.*", "", response, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": "วิเคราะห์เสร็จสิ้น เรียบร้อยครับ"}]
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

# 7. UI Display
if st.session_state.rep:
    st.divider()
    # แสดงผลแยกส่วนโดยใช้ Expander หรือ Container
    st.markdown(st.session_state.rep)
    
    if st.session_state.qs:
        st.markdown("<p class='q-lbl'>💡 คำถามที่แนะนำให้ถามช่าง:</p>", unsafe_allow_html=True)
        q_cols = st.columns(len(st.session_state.qs))
        for idx, q_text in enumerate(st.session_state.qs):
            if q_cols[idx].button(f"💬 {q_text}", key=f"btn_{idx}"):
                run_q(q_text)
                st.rerun()

    # Chat History
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if u_input := st.chat_input("สอบถามรายละเอียดเพิ่มเติม..."):
        run_q(u_input)
        st.rerun()

st.markdown("<div class='maroon'><strong>หมายเหตุ:</strong> ระบบนี้เป็นการวิเคราะห์เบื้องต้นทางวิศวกรรมด้วย AI เท่านั้น ไม่สามารถนำไปใช้อ้างอิงทางกฎหมาย หรือทดแทนการตรวจสอบโดยวิศวกรวิชาชีพ ณ หน้างานจริงได้</div>", unsafe_allow_html=True)
