import streamlit as st
from PIL import Image

# --- 1. CONFIG (ลบความเป็น Streamlit ออก) ---
st.set_page_config(
    page_title="BHOON KHARN - Construction AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. THEME & BRANDING (Bhoon Kharn Identity) ---
st.markdown("""
<style>
    /* ปรับแต่งโทนสีแบรนด์ */
    :root {
        --bk-gold: #B59473;
        --bk-dark: #1E1A17;
        --bk-brown: #4A3F35;
        --text-light: #F5F5F5;
    }

    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    html, body, [class*="st-app"] { 
        background-color: var(--bk-dark); 
        color: var(--text-light); 
        font-family: 'Inter', 'Sarabun', sans-serif; 
    }
    
    /* ระบบไฟสถานะมุมขวาบน */
    .status-bar { position: fixed; top: 20px; right: 30px; display: flex; align-items: center; gap: 10px; z-index: 1000; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background-color: #28a745; box-shadow: 0 0 8px #28a745; }
    .status-text { font-size: 0.7rem; font-weight: 700; color: var(--bk-gold); letter-spacing: 1.5px; }
    
    /* Branding */
    .bk-title { font-size: 3rem; font-weight: 700; text-align: center; letter-spacing: -1.5px; margin-top: 60px; color: var(--bk-gold); }
    .bk-subtitle { font-size: 0.85rem; color: #888; text-align: center; margin-bottom: 50px; text-transform: uppercase; letter-spacing: 5px; }
    
    /* ปรับแต่งช่อง Upload ให้เล็กลงและเรียบหรู */
    .stFileUploader { border: 1px solid #333; border-radius: 12px; background: rgba(255,255,255,0.02); }
    .stFileUploader section { padding: 0.5rem !important; }
    
    /* ปุ่มรันสีทอง (Identity Color) */
    div.stButton > button {
        background-color: var(--bk-gold) !important;
        color: var(--bk-dark) !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 8px !important;
        transition: 0.3s !important;
    }
    div.stButton > button:hover {
        background-color: #D4AF37 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(181, 148, 115, 0.3);
    }
</style>

<div class="status-bar">
    <div class="dot"></div> <span class="status-text">ONLINE</span>
</div>
""", unsafe_allow_html=True)

# --- 3. NAVIGATION ---
nav_l, nav_r = st.columns([8, 2])
with nav_r:
    c_lang, c_user = st.columns([1, 1.2])
    with c_lang: st.button("🌐 TH")
    with c_user:
        with st.popover("👤"):
            st.markdown(f"**Jom Kokeattrakool**")
            st.divider()
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            st.button("Sign Out", type="primary", use_container_width=True)

# --- 4. MAIN LAYOUT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
st.markdown("<div class='bk-subtitle'>Advanced Construction Intelligence</div>", unsafe_allow_html=True)

st.divider()

# อัปโหลด & พรีวิว
up_col1, up_col2 = st.columns(2)

with up_col1:
    st.markdown("<p style='font-size:0.85rem; color:#888; font-weight:bold;'>1. BLUEPRINT / PLAN</p>", unsafe_allow_html=True)
    file_plan = st.file_uploader("a", label_visibility="collapsed", type=['jpg','png','pdf'])
    if file_plan and file_plan.type != "application/pdf":
        st.image(file_plan, width=150, caption="Preview Plan")

with up_col2:
    st.markdown("<p style='font-size:0.85rem; color:#888; font-weight:bold;'>2. SITE PHOTO</p>", unsafe_allow_html=True)
    file_site = st.file_uploader("b", label_visibility="collapsed", type=['jpg','png'])
    if file_site:
        st.image(file_site, width=150, caption="Preview Site")

st.markdown("<br>", unsafe_allow_html=True)

# ปุ่มรัน
_, btn_center, _ = st.columns([1, 1.5, 1])
with btn_center:
    if st.button("RUN ANALYSIS", use_container_width=True):
        if file_plan or file_site:
            with st.spinner("BHOON KHARN AI กำลังประมวลผล..."):
                # จำลองการทำงาน (ในอนาคตคือส่วนเชื่อมต่อ Gemini)
                import time
                time.sleep(2)
                st.balloons()
                st.success("วิเคราะห์ข้อมูลสำเร็จ! (นี่คือการทดสอบระบบ UI)")
                
                # Mockup ผลลัพธ์เบื้องต้น
                st.markdown("### 🔍 ผลการวิเคราะห์เบื้องต้น")
                st.info("AI ตรวจพบโครงสร้างพื้นฐานในรูปภาพ กำลังจัดเตรียมข้อมูลวัสดุ...")
        else:
            st.warning("กรุณาอัปโหลดรูปภาพเพื่อเริ่มการวิเคราะห์")

st.markdown(f"<div style='text-align:center; margin-top:150px; color:#444; font-size:0.7rem; letter-spacing:2px;'>BHOON KHARN © 2026 | ALL RIGHTS RESERVED</div>", unsafe_allow_html=True)
