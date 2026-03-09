import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: จัดการความสะอาดตา สีตัวอักษร และลดขนาดส่วนถามต่อ
st.markdown("""
    <style>
    .disclaimer-text {
        color: #8B0000; /* สีแดงเลือดหมู */
        font-size: 0.8rem;
        line-height: 1.4;
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    .check-box {
        padding: 5px 0 5px 20px;
        border-left: 4px solid #1E3A8A;
        margin-bottom: 25px;
        color: #31333F; /* สีมาตรฐาน */
        line-height: 1.8;
    }
    /* ปุ่มคำถามด่วน: เล็กและสะอาดตา */
    .stButton>button {
        font-size: 0.75rem !important; 
        padding: 2px 8px !important;
        min-height: 26px !important;
        height: 26px !important;
        border-radius: 4px !important;
    }
    .quick-q-label {
        font-size: 0.75rem !important;
        color: #888;
        margin-bottom: 5px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการ API Key
def get_working_keys():
    keys = []
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "GOOGLE_API_KEY" in k and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "ไม่พบ API Key"
    shuffled = keys.copy()
    random.shuffle(shuffled)
    for k in shuffled:
        try:
            genai.configure(api_key=k)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0] if models else None
            if not target: continue
            model = genai.GenerativeModel(target)
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    engine, status = init_engine(get_working_keys())
    st.session_state.engine = engine
    st.session_state.status = status

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar
with st.sidebar:
    st.title("⚙️ การตั้งค่าระบบ")
    if st.session_state.engine: st.success("🟢 ระบบพร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status', 'ขัดข้อง')}")
    
    if st.button("🔄 รีเซ็ตระบบ"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ (ประจำที่แน่นอน)
col_l, col_r = st.columns(2)
with col_l:
    blueprint = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
    if blueprint: st.image(blueprint, caption="แบบอ้างอิง", use_container_width=True)
with col_r:
    site_photo = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_photo: st.image(site_photo, caption="หน้างานจริง", use_container_width=True)

# ฟังก์ชันส่งคำถามต่อเนื่อง
def run_query(q):
    if not st.session_state.engine: return
    st.session_state.chat_history.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content(f"วิเคราะห์ในฐานะ BHOON KHARN: {q}")
    st.session_state.chat_history.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site_photo or blueprint:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                prompt = f"""
                วิเคราะห์ภาพในฐานะที่ปรึกษา BHOON KHARN โดยเริ่มทันที:
                🔍 [วิเคราะห์หน้างาน]: (ระบุงานและสถานะ)
                ⏱️ [จุดตายวิกฤต]: (ความเสี่ยงแฝง)
                ⚠️ [ผลกระทบต่อเนื่อง]: (Domino Effect และงบซ่อม)
                🏗️ [มาตรฐานเทคนิค]: (วสท./มยผ./สากล)
                🏠 [จุดสังเกตสำคัญสำหรับเจ้าของบ้าน]: 
                (สรุปเป็นข้อๆ โดยใช้ Emoji นำหน้า และต้องขึ้นบรรทัดใหม่ 2 ครั้งทุกครั้งที่จบข้อเพื่อให้อ่านง่าย)
                
                แนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:' (ห้ามแสดงหัวข้อคำถามในเนื้อหา)
                โหมด: {mode}
                """
                imgs = [Image.open(f) for f in [blueprint, site_photo] if f]
                resp = st.session_state.engine.generate_content([prompt] + imgs)
                full_text = resp.text
                
                found_qs = re.findall(r"ถามช่าง: (.+)", full_text)
                st.session_state.quick_qs = [q.strip() for q in found_qs[:3]]
                clean_report = re.sub(r"ถามช่าง: .*", "", full_text).strip()
                
                st.session_state.final_report = clean_report
                st.session_state.chat_history = [{"role": "assistant", "content": clean_report}]
                st.rerun()
            except Exception as e: st.error(f"ผิดพลาด: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# --- 6. ส่วน
