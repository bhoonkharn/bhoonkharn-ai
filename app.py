import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บและ Branding
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ API Key
def get_keys():
    keys = []
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "GOOGLE_API_KEY" in k and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

# 3. โหลดโมเดลอัจฉริยะ (White Label)
@st.cache_resource
def init_ai(keys):
    if not keys: return None, "ไม่พบกุญแจในระบบ"
    random.shuffle(keys)
    for k in keys:
        try:
            genai.configure(api_key=k)
            # ค้นหาโมเดลที่ใช้ได้จริง
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0] if models else None
            if not target: continue
            model = genai.GenerativeModel(target)
            model.generate_content("test")
            return model, "พร้อมวิเคราะห์"
        except: continue
    return None, "กุญแจใช้งานไม่ได้"

if "active_model" not in st.session_state:
    m, s = init_ai(get_keys())
    st.session_state.active_model = m
    st.session_state.status = s

model = st.session_state.active_model

if "messages" not in st.session_state: st.session_state.messages = []
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "suggested_q" not in st.session_state: st.session_state.suggested_q = []

# 4. แถบเครื่องมือทางซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if model: st.success("🟢 ระบบพร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status', 'ขัดข้อง')}")
    
    if st.button("🔄 พยายามเชื่อมต่อใหม่"):
        st.session_state.active_model = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 วิเคราะห์เชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติทั้งหมด", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.session_state.suggested_q = []
        st.rerun()

# 5. ส่วนอัปโหลด
c1, c2 = st.columns(2)
with c1: b_file = st.file_uploader("แบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
with c2: s_file = st.file_uploader("ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])

# ฟังก์ชันจัดการคำถาม
def ask_ai(query):
    if not model: return
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"): st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์..."):
            res = model.generate_content(f"วิเคราะห์เชิงลึกในฐานะ BHOON KHARN: {query}")
            st.markdown(res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {res.text}"
            st.session_state.messages.append({"role": "assistant", "content": res.text})

# 6. เริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not model: st.error("กรุณาเชื่อมต่อ API")
    elif s_file or b_file:
        with st.spinner('กำลังประมวลผล...'):
            try:
                prompt = f"""
                ห้ามแนะนำตัว ห้ามทักทาย ให้เริ่มรายงานทันทีดังนี้:
                🔍 [วิเคราะห์หน้างาน]: ระบุงานและสถานะปัจจุบัน
                ⏱️ [ปัจจัยวิกฤต]: ตรวจสอบเวลา/อายุวัสดุ/ความเสี่ยงที่มองไม่เห็น
                ⚠️ [ผลกระทบต่อเนื่อง]: Domino Effect และผลเสียต่องบประมาณ
                🏗️ [มาตรฐานเทคนิค]: มาตรฐานสากล/วสท. ที่เกี่ยวข้อง
                🏠 [มุมเจ้าของบ้าน]: วิธีเช็คเอง 1-2-3 (ภาษาง่ายๆ)
                💬 [คำถามชวนคุยต่อ]: แนะนำ 3 คำถามที่ขึ้นต้นด้วย 'ถามช่าง:'
                รูปแบบ: {mode}
                """
                imgs = [Image.open(f) for f in [b_file, s_file] if f]
                resp = model.generate_content([prompt] + imgs)
                st.session_state.messages = [{"role": "assistant", "content": resp.text}]
                st.session_state.full_report = resp.text
                qs = re.findall(r"ถามช่าง: (.+)", resp.text)
                st.session_state.suggested_q = [q.strip() for q in qs[:3]]
                st.rerun()
            except Exception as e: st.error(f"ผิดพลาด: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผล
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 รายงานจาก BHOON KHARN AI")
    st.download_button("📥 บันทึกรายงาน", st.session_state.full_report, "BK_Report.txt")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if st.session_state.suggested_q:
        st.info("💡 **คลิกเพื่อถามรายละเอียดเพิ่ม:**")
        for q in st.session_state.suggested_q:
            if st.button(f"🔎 {q}", key=f"q_{hash(q)}", use_container_width=True):
                ask_ai(q)
                st.rerun()

    if p_chat := st.chat_input("พิมพ์ถามเพิ่ม..."):
        ask_ai(p_chat)
    st.caption("🚨 หมายเหตุ: รายงานเบื้องต้น โปรดปรึกษาวิศวกรหน้างานอีกครั้ง")
