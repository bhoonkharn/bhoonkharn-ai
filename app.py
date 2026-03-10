import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 20px; }
    .stAlert { border-radius: 10px; border: none; }
    .owner-box { 
        background-color: #f0f4f8; 
        border-left: 5px solid #1E3A8A; 
        padding: 20px; 
        border-radius: 5px; 
        margin: 10px 0;
    }
    .q-suggest { font-size: 0.85rem; color: #1E3A8A; font-weight: bold; margin-bottom: 10px; }
    div.stButton > button { 
        border-radius: 20px; 
        font-size: 0.8rem !important; 
        transition: all 0.3s;
    }
    .footer-note { color: #8B0000; font-size: 0.75rem; text-align: center; margin-top: 50px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (API MANAGEMENT) ---
def get_all_keys():
    """ดึง API Keys ทั้งหมดจาก Secrets"""
    keys = []
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    # ดึงคีย์สำรองอื่นๆ ที่อาจตั้งชื่อต่างกัน
    for k in st.secrets.keys():
        if "API_KEY" in k.upper() and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

def try_init_model(api_key):
    """พยายามเชื่อมต่อ Model ตามลำดับความเสถียร"""
    genai.configure(api_key=api_key)
    # ลำดับรุ่นที่ต้องการใช้ (Flash-8b มี Quota สูงสุด)
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.0-flash-exp"]
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            model.generate_content("test", generation_config={"max_output_tokens": 5})
            return model, m_name
        except Exception:
            continue
    return None, None

@st.cache_resource
def load_engine():
    keys = get_all_keys()
    if not keys:
        return None, "❌ ไม่พบ API Key ใน System Secrets"
    
    random.shuffle(keys) # กระจายโหลด
    for key in keys:
        model, model_name = try_init_model(key)
        if model:
            return model, f"✅ เชื่อมต่อสำเร็จ ({model_name})"
    
    return None, "❌ Quota เต็มทุก Key หรือการเชื่อมต่อมีปัญหา"

# Initialize Session States
for key in ["chat_history", "analysis_result", "suggested_qs"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key != "analysis_result" else ""

# --- 3. SIDEBAR & TOOLS ---
with st.sidebar:
    st.markdown("### ⚙️ แผงควบคุม")
    engine, status_msg = load_engine()
    
    if "✅" in status_msg: st.success(status_msg)
    else: st.error(status_msg)
    
    if st.button("🔄 รีเฟรชการเชื่อมต่อ"):
        st.cache_resource.clear()
        st.rerun()
        
    st.divider()
    mode = st.radio("มุมมองการวิเคราะห์:", ["📊 เชิงวิศวกรรม/เทคนิค", "🏠 สำหรับเจ้าของบ้าน"])
    
    if st.button("🗑️ ล้างประวัติทั้งหมด"):
        st.session_state.chat_history = []
        st.session_state.analysis_result = ""
        st.session_state.suggested_qs = []
        st.rerun()

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.caption("<center>ระบบตรวจงานก่อสร้างอัจฉริยะ วิเคราะห์แปลนและหน้างานด้วยวิศวกรรม AI</center>", unsafe_allow_html=True)

col_up1, col_up2 = st.columns(2)
with col_up1:
    bp_file = st.file_uploader("📋 อัปโหลดแบบแปลน (Blueprint)", type=['jpg','jpeg','png'])
with col_up2:
    site_file = st.file_uploader("📸 อัปโหลดรูปหน้างานจริง", type=['jpg','jpeg','png'])

# --- 5. LOGIC FUNCTIONS ---
def analyze_images():
    if not engine:
        st.error("AI Engine ไม่พร้อมทำงาน กรุณาเช็ค API Key")
        return

    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์ข้อมูล..."):
        try:
            prompt = f"""คุณคือ BHOON KHARN AI วิศวกรผู้เชี่ยวชาญ 
            วิเคราะห์ภาพที่แนบมาในโหมด: {mode}
            สรุปหัวข้อดังนี้:
            1. [ANALYSIS] วิเคราะห์สิ่งที่เห็น
            2. [RISK] จุดที่อันตรายหรือต้องแก้ไขด่วน
            3. [STANDARD] มาตรฐานวิศวกรรมที่เกี่ยวข้อง
            4. [OWNER_NOTE] คำแนะนำสำคัญสำหรับเจ้าของบ้าน
            5. [QUESTIONS] คำแนะนำ 3 คำถามที่ควรใช้ถามช่าง (ขึ้นต้นด้วย 'ถามช่าง: ')"""
            
            inputs = [prompt]
            if bp_file: inputs.append(Image.open(bp_file))
            if site_file: inputs.append(Image.open(site_file))
            
            response = engine.generate_content(inputs).text
            
            # Extract Questions
            questions = re.findall(r"ถามช่าง:\s*(.*)", response)
            st.session_state.suggested_qs = [q.strip() for q in questions[:3]]
            
            # Clean Report
            report = re.sub(r"ถามช่าง:.*", "", response, flags=re.DOTALL).strip()
            st.session_state.analysis_result = report
            st.session_state.chat_history = [{"role": "assistant", "content": "วิเคราะห์ภาพเสร็จสิ้น คุณสามารถสอบถามข้อมูลเพิ่มเติมได้จากช่องแชทด้านล่างครับ"}]
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}")

def ask_ai(query):
    if engine:
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.spinner("AI กำลังพิมพ์..."):
            res = engine.generate_content(f"Context: BHOON KHARN AI. Question: {query}")
            st.session_state.chat_history.append({"role": "assistant", "content": res.text})

# --- 6. DISPLAY RESULTS ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp_file or site_file:
        analyze_images()
    else:
        st.warning("⚠️ กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูปก่อนเริ่มวิเคราะห์")

if st.session_state.analysis_result:
    st.divider()
    res_text = st.session_state.analysis_result
    
    # แสดงผลแยกตาม Section ที่ตรวจพบ
    sections = {
        "🔍 วิเคราะห์": "[ANALYSIS]",
        "⏱️ จุดวิกฤต/ความเสี่ยง": "[RISK]",
        "🏗️ มาตรฐานวิศวกรรม": "[STANDARD]",
        "🏠 ข้อควรระวังสำหรับเจ้าของบ้าน": "[OWNER_NOTE]"
    }
    
    for label, tag in sections.items():
        if tag in res_text or tag.lower() in res_text.lower():
            content = res_text.split(tag)[-1].split("[")[0].strip().strip(":")
            if tag == "[OWNER_NOTE]":
                st.markdown(f"### {label}")
                st.markdown(f"<div class='owner-box'>{content}</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{label}**", expanded=True if tag=="[ANALYSIS]" else False):
                    st.write(content)

    # Suggested Questions Buttons
    if st.session_state.suggested_qs:
        st.markdown("<p class='q-suggest'>💡 คำถามที่แนะนำให้ถามทีมช่าง:</p>", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.suggested_qs))
        for i, q in enumerate(st.session_state.suggested_qs):
            if cols[i].button(f"🔎 {q}", key=f"sq_{i}", use_container_width=True):
                ask_ai(q)
                st.rerun()

    # Chat UI
    st.divider()
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("พิมพ์คำถามเพิ่มเติมที่นี่..."):
        ask_ai(prompt)
        st.rerun()

st.markdown("""
<div class='footer-note'>
    <strong>คำเตือน:</strong> การวิเคราะห์นี้เป็นเพียงการประมวลผลเบื้องต้นจากรูปภาพ <br> 
    ไม่สามารถทดแทนการตรวจสอบหน้างานโดยวิศวกรวิชาชีพ (PE/SE) ได้
</div>
""", unsafe_allow_html=True)
