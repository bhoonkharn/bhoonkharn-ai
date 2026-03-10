import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# --- 1. CONFIG & STYLE (ธีม BHOON KHARN AI) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #666; margin-bottom: 25px; font-size: 0.9rem; }
    .owner-box { 
        background-color: #f0f4f8; 
        border-left: 5px solid #1E3A8A; 
        padding: 18px; 
        border-radius: 5px; 
        margin: 10px 0;
    }
    .stButton > button { border-radius: 20px; transition: 0.3s; }
    .footer-note { color: #8B0000; font-size: 0.75rem; text-align: center; margin-top: 50px; opacity: 0.7; border-top: 1px solid #eee; padding-top: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบแก้ปัญหา 404 & Quota) ---
def get_api_key():
    """ดึง Key จาก Secrets อย่างปลอดภัย"""
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    for k in st.secrets.keys():
        if "API_KEY" in k.upper(): return st.secrets[k]
    return None

def init_ai_engine():
    """เชื่อมต่อ AI พร้อมระบบ Fallback ป้องกัน Error 404"""
    api_key = get_api_key()
    if not api_key:
        return None, "❌ ไม่พบ API Key ในหน้า Secrets"
    
    try:
        genai.configure(api_key=api_key)
        
        # รายชื่อ Model ที่จะลองเรียกตามลำดับ (ป้องกัน 404 models/gemini-1.5-flash is not found)
        models_to_try = [
            "gemini-1.5-flash-latest", 
            "gemini-1.5-flash", 
            "gemini-1.5-pro-latest",
            "gemini-2.0-flash-exp"
        ]
        
        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(m_name)
                # ลอง Ping สั้นๆ เพื่อเช็คว่า Model นี้มีอยู่จริงและรองรับ API นี้ไหม
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, f"✅ ระบบพร้อมใช้งาน ({m_name})"
            except Exception:
                continue # ถ้าพัง (404) ให้ไปลองตัวถัดไป
                
        return None, "❌ ติดต่อ Model ไม่ได้ (อาจเกิดจาก API Version ไม่รองรับ)"
    except Exception as e:
        return None, f"❌ ข้อผิดพลาด: {str(e)}"

# ตรวจสอบสถานะการเชื่อมต่อ
if "engine" not in st.session_state or st.session_state.engine is None:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# ค่าตั้งต้นของ Session
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analysis_result" not in st.session_state: st.session_state.analysis_result = ""
if "suggested_qs" not in st.session_state: st.session_state.suggested_qs = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    st.info(st.session_state.status)
    
    if st.button("🔄 ลองเชื่อมต่อใหม่ (Reconnect)", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
        
    st.divider()
    mode = st.radio("เลือกมุมมองการวิเคราะห์:", ["📊 เชิงเทคนิค/วิศวกรรม", "🏠 สำหรับเจ้าของบ้าน"])
    
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.analysis_result = ""
        st.session_state.suggested_qs = []
        st.rerun()

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>ระบบวิเคราะห์งานก่อสร้างอัจฉริยะ โดย บุญกาญจน์</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    bp_file = st.file_uploader("📋 แนบรูปแปลน (ถ้ามี)", type=['jpg','jpeg','png'])
    if bp_file: st.image(bp_file, caption="แบบแปลน")
with col2:
    site_file = st.file_uploader("📸 แนบรูปหน้างานจริง", type=['jpg','jpeg','png'])
    if site_file: st.image(site_file, caption="สภาพหน้างาน")

# --- 5. LOGIC & PROCESSING ---
def run_analysis():
    if not st.session_state.engine:
        st.error("AI ยังไม่พร้อมทำงาน กรุณาเช็ค API Key")
        return

    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            prompt = f"""คุณคือ BHOON KHARN AI ผู้เชี่ยวชาญด้านงานก่อสร้าง 
            วิเคราะห์ภาพที่แนบมาในโหมด: {mode}
            ตอบเป็นภาษาไทยตามโครงสร้างนี้:
            [ANALYSIS] (วิเคราะห์สิ่งที่พบในรูป)
            [RISK] (จุดเสี่ยงหรือสิ่งที่ต้องแก้ไขด่วน)
            [STANDARD] (อ้างอิงมาตรฐานงานช่าง/วิศวกรรม)
            [OWNER_NOTE] (คำแนะนำที่เจ้าของบ้านควรทราบ)
            จากนั้นแนะนำ 3 คำถามที่ควรใช้ถามช่าง (ขึ้นต้นด้วย 'ถามช่าง: ' ทุกข้อ)"""
            
            payload = [prompt]
            if bp_file: payload.append(Image.open(bp_file))
            if site_file: payload.append(Image.open(site_file))
            
            response = st.session_state.engine.generate_content(payload)
            full_text = response.text
            
            # ดึงคำถามแนะนำ
            qs = re.findall(r"ถามช่าง:\s*(.*)", full_text)
            st.session_state.suggested_qs = [q.strip() for q in qs[:3]]
            
            # บันทึกผลวิเคราะห์หลัก
            st.session_state.analysis_result = re.sub(r"ถามช่าง:.*", "", full_text, flags=re.DOTALL).strip()
            
        except Exception as e:
            st.error(f"AI ประมวลผลไม่ได้: {str(e)}")

def ask_ai(q):
    if st.session_state.engine:
        with st.spinner("AI กำลังคิดคำตอบ..."):
            try:
                res = st.session_state.engine.generate_content(f"ในฐานะ BHOON KHARN AI: {q}")
                st.session_state.chat_history.append({"role": "user", "content": q})
                st.session_state.chat_history.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 6. DISPLAY RESULTS ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp_file or site_file:
        run_analysis()
    else:
        st.warning("⚠️ กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูป")

if st.session_state.analysis_result:
    st.divider()
    res = st.session_state.analysis_result
    
    # แบ่งแสดงผลเป็นกล่องๆ ตาม Tag
    sections = [
        ("🔍 วิเคราะห์หน้างาน", "[ANALYSIS]"),
        ("⏱️ จุดตายวิกฤต/ความเสี่ยง", "[RISK]"),
        ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"),
        ("🏠 ข้อสังเกตสำหรับเจ้าของบ้าน", "[OWNER_NOTE]")
    ]
    
    for title, tag in sections:
        if tag in res:
            content = res.split(tag)[1].split("[")[0].strip()
            if tag == "[OWNER_NOTE]":
                st.markdown(f"<div class='owner-box'><strong>{title}</strong><br>{content}</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{title}**", expanded=True if tag=="[ANALYSIS]" else False):
                    st.write(content)

    # ปุ่มคำถามแนะนำ
    if st.session_state.suggested_qs:
        st.write("---")
        st.markdown("**💡 ถาม BHOON KHARN AI ต่อ:**")
        cols = st.columns(len(st.session_state.suggested_qs))
        for i, q in enumerate(st.session_state.suggested_qs):
            if cols[i].button(f"💬 {q}", key=f"btn_{i}", use_container_width=True):
                ask_ai(q)
                st.rerun()

    # Chat UI
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_q := st.chat_input("สอบถามรายละเอียดเพิ่มเติมได้ที่นี่..."):
        ask_ai(user_q)
        st.rerun()

st.markdown("<div class='footer-note'><strong>Note:</strong> ประเมินเบื้องต้นจากรูปภาพเท่านั้น ไม่สามารถใช้แทนการตรวจหน้างานจริงโดยวิศวกรวิชาชีพได้</div>", unsafe_allow_html=True)
