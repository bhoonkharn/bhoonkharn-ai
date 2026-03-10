import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 20px; }
    .owner-box { 
        background-color: #f0f4f8; 
        border-left: 5px solid #1E3A8A; 
        padding: 20px; 
        border-radius: 5px; 
        margin: 10px 0;
    }
    .footer-note { color: #8B0000; font-size: 0.75rem; text-align: center; margin-top: 50px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบเชื่อมต่อแบบ Direct) ---
def get_api_key():
    """ดึง Key จาก Secrets"""
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    # ถ้าหาไม่เจอ ให้ลองหาตัวแปรอื่นที่มีคำว่า API_KEY
    for k in st.secrets.keys():
        if "API_KEY" in k.upper():
            return st.secrets[k]
    return None

def init_ai_engine():
    """เชื่อมต่อ Google AI แบบข้ามการทดสอบเพื่อเลี่ยง Quota Error"""
    api_key = get_api_key()
    if not api_key:
        return None, "❌ ไม่พบ API Key ในหน้า Secrets (Settings)"
    
    try:
        genai.configure(api_key=api_key)
        # ใช้รุ่น Flash เพราะวิเคราะห์ภาพได้ดีและ Quota เยอะ
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model, "✅ ระบบพร้อมทำงาน"
    except Exception as e:
        return None, f"❌ เกิดข้อผิดพลาด: {str(e)}"

# โหลด Engine ครั้งเดียว
if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# ค่าตั้งต้นอื่นๆ
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analysis_result" not in st.session_state: st.session_state.analysis_result = ""
if "suggested_qs" not in st.session_state: st.session_state.suggested_qs = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ การตั้งค่า")
    st.info(st.session_state.status)
    
    if st.button("🔄 ลองเชื่อมต่อใหม่"):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
        
    mode = st.radio("โหมดการวิเคราะห์:", ["📊 เชิงวิศวกรรม/เทคนิค", "🏠 สำหรับเจ้าของบ้าน"])
    
    if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
        st.session_state.chat_history = []
        st.session_state.analysis_result = ""
        st.session_state.suggested_qs = []
        st.rerun()

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

col_up1, col_up2 = st.columns(2)
with col_up1:
    bp_file = st.file_uploader("📋 รูปแบบแปลน (Blueprint)", type=['jpg','jpeg','png'])
    if bp_file: st.image(bp_file, caption="แบบแปลนที่อัปโหลด")
with col_up2:
    site_file = st.file_uploader("📸 รูปหน้างานจริง", type=['jpg','jpeg','png'])
    if site_file: st.image(site_file, caption="รูปหน้างานที่อัปโหลด")

# --- 5. LOGIC ---
def run_analysis():
    if not st.session_state.engine:
        st.error("กรุณาตั้งค่า API Key ให้ถูกต้องก่อน")
        return

    with st.spinner("AI กำลังวิเคราะห์ภาพ..."):
        try:
            prompt = f"""คุณคือ BHOON KHARN AI วิศวกรผู้เชี่ยวชาญการตรวจงานก่อสร้าง
            วิเคราะห์ภาพในโหมด: {mode}
            ตอบตามหัวข้อดังนี้:
            [ANALYSIS] วิเคราะห์สิ่งที่เห็น
            [RISK] จุดวิกฤตที่ต้องระวัง
            [STANDARD] มาตรฐานวิศวกรรม
            [OWNER_NOTE] คำแนะนำสำหรับเจ้าของบ้าน
            จากนั้นแนะนำ 3 คำถามที่ควรใช้ถามช่าง โดยขึ้นต้นว่า 'ถามช่าง: ' ทุกข้อ"""
            
            inputs = [prompt]
            if bp_file: inputs.append(Image.open(bp_file))
            if site_file: inputs.append(Image.open(site_file))
            
            # เรียกใช้ AI
            response = st.session_state.engine.generate_content(inputs)
            text_res = response.text
            
            # แยกคำถามแนะนำ
            qs = re.findall(r"ถามช่าง:\s*(.*)", text_res)
            st.session_state.suggested_qs = [q.strip() for q in qs[:3]]
            
            # บันทึกผลวิเคราะห์ (ตัดคำถามออก)
            st.session_state.analysis_result = re.sub(r"ถามช่าง:.*", "", text_res, flags=re.DOTALL).strip()
            
        except Exception as e:
            st.error(f"AI ตอบกลับไม่ได้: {str(e)}")
            if "quota" in str(e).lower():
                st.warning("คำแนะนำ: โควตาฟรีของคุณหมดชั่วคราว กรุณารอ 1-2 นาทีแล้วลองใหม่ครับ")

def ask_more(q_text):
    if st.session_state.engine:
        with st.spinner("กำลังหาคำตอบ..."):
            try:
                res = st.session_state.engine.generate_content(f"ในฐานะ BHOON KHARN AI: {q_text}")
                st.session_state.chat_history.append({"role": "user", "content": q_text})
                st.session_state.chat_history.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp_file or site_file:
        run_analysis()
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

if st.session_state.analysis_result:
    st.divider()
    # แสดงผลแยกกล่องเพื่อให้ดูง่าย
    res = st.session_state.analysis_result
    
    # ดึงข้อมูลมาโชว์ทีละส่วน (Simple Split)
    parts = res.split("[")
    for p in parts:
        if "ANALYSIS]" in p:
            st.info("**🔍 วิเคราะห์หน้างาน**\n\n" + p.replace("ANALYSIS]", "").strip())
        elif "RISK]" in p:
            st.warning("**⏱️ จุดวิกฤตที่ต้องระวัง**\n\n" + p.replace("RISK]", "").strip())
        elif "STANDARD]" in p:
            with st.expander("🏗️ มาตรฐานวิศวกรรม"):
                st.write(p.replace("STANDARD]", "").strip())
        elif "OWNER_NOTE]" in p:
            st.markdown(f"<div class='owner-box'><strong>🏠 ข้อแนะนำสำหรับเจ้าของบ้าน:</strong><br><br>{p.replace('OWNER_NOTE]', '').strip()}</div>", unsafe_allow_html=True)

    # ปุ่มคำถามแนะนำ
    if st.session_state.suggested_qs:
        st.write("---")
        st.markdown("**💡 ลองถาม AI ต่อ:**")
        q_cols = st.columns(len(st.session_state.suggested_qs))
        for i, q in enumerate(st.session_state.suggested_qs):
            if q_cols[i].button(f"💬 {q}", key=f"q_{i}"):
                ask_more(q)
                st.rerun()

    # Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if u_input := st.chat_input("พิมพ์คำถามเพิ่มเติม..."):
        ask_more(u_input)
        st.rerun()

st.markdown("<div class='footer-note'>หมายเหตุ: ผลวิเคราะห์นี้เป็นเพียงการให้คำแนะนำเบื้องต้น ไม่สามารถใช้อ้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
