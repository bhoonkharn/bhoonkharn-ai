import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE (ล้างฉากหลังและปรับสีตัวอักษรให้มาตรฐาน 100%) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Sarabun', sans-serif; 
        line-height: 1.8; 
    }
    
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 30px; }
    
    /* หัวข้อ Section */
    .section-header {
        color: #1E3A8A;
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
        border-bottom: 2px solid #eee;
        padding-bottom: 5px;
    }

    /* โหมดเจ้าของบ้าน - ล้างฉากหลัง ใช้สีและฟอนต์มาตรฐานเดียวกับระบบ */
    .owner-content { 
        border-left: 5px solid #1E3A8A; 
        padding-left: 20px; 
        margin: 20px 0;
        background: transparent !important; /* บังคับไม่มีฉากหลัง */
        color: inherit !important; /* ใช้สีเดียวกับข้อความปกติของแอป */
        font-size: 1rem; /* ขนาดเท่ากับข้อความปกติ */
    }
    
    /* ปุ่มคำถามชวนคุย (จิ๋ว 0.7rem) */
    div.stButton > button { 
        font-size: 0.75rem !important; 
        border-radius: 10px !important;
        color: #555 !important;
    }

    /* หมายเหตุสีแดงเลือดหมู */
    .maroon-note { 
        color: #8B0000; 
        font-size: 0.85rem; 
        border-top: 1px solid #eee; 
        margin-top: 40px; 
        padding-top: 20px; 
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (BHOON KHARN AI ONLY) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "กรุณาตั้งค่า API Key"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        return model, "เชื่อมต่อสำเร็จ"
    except Exception:
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name), "เชื่อมต่อสำเร็จ"
        except: pass
        return None, "การเชื่อมต่อขัดข้อง"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    if "สำเร็จ" in st.session_state.status:
        st.success(st.session_state.status)
    else:
        st.error(st.session_state.status)
        
    if st.button("🔄 เริ่มต้นระบบใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_en
