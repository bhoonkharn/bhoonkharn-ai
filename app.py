import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG (International Standard) ---
st.set_page_config(
    page_title="BHOON KHARN - Construction AI Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CSS (Precision Styling) ---
st.markdown("""
<style>
    /* ปิด Sidebar และส่วนเกิน */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Bhoon Kharn Theme */
    :root { --gold: #B59473; --dark: #1E1A17; --light-gold: #D4AF37; }
    html, body, [class*="st-app"] { background-color: var(--dark); color: #F5F5F5; font-family: 'Inter', sans-serif; }
    
    /* 1. Slim Header & Buttons (แก้จุดที่ 1: Login ใหญ่เกินไป) */
    .top-nav { position: fixed; top: 15px; right: 30px; display: flex; align-items: center; gap: 10px; z-index: 1000; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #28a745; margin-right: 5px; }
    
    /* บีบขนาดปุ่มใน Navigation ให้เล็กลงพิเศษ */
    div[data-testid="stColumn"] button {
        padding: 2px 12px !important;
        font-size: 0.75rem !important;
        min-height: 30px !important;
        border-radius: 4px !important;
        text-transform: uppercase;
    }

    /* 2. Branding Section */
    .bk-title { font-size: 2.5rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 30px; color: var(--gold); }
    .bk-subtitle { font-size: 0.75rem; color: #888; text-align: center; margin-bottom: 40px; text-transform: uppercase; letter-spacing: 5px; }
    
    /* 3. Proportional Uploaders & Image Frame (แก้จุดที่ 2: รูปอัพแล้วไม่สมส่วน) */
    .stFileUploader { max-width: 100%; }
    .stFileUploader section { padding: 0.5rem !important; min-height: 70px !important; border: 1px dashed #444 !important; }
    
    /* กรอบรูป Preview ให้ดูเป็นระเบียบ */
    .preview-container {
        display: flex;
        justify-content: center;
        align-items: center;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 10px;
        background: rgba(255,255,255,0.02);
        margin-top: 10px;
        min-height: 150px;
    }
    
    /* ปุ่มวิเคราะห์ (Identity) */
    .stButton > button[kind="primary"] {
        background-color: var(--gold) !important;
        color: var(--dark) !important;
        border: none !important;
        font-size: 0.9rem !important;
        padding: 10px 40px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 4. NAVIGATION BAR ---
# ใช้ columns เพื่อจัดวางปุ่มขนาดเล็กมุมขวา
nav_l, nav_lang, nav_user = st.columns([9, 0.4, 0.6])

with nav_lang:
    if st.button(st.session_state.lang):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()

with nav_user:
    if not st.session_state.logged_in:
        if st.button("SIGN IN"):
            st.session_state.logged_in = True
            st.rerun()
    else:
        with st.popover("👤"):
            st.markdown(f"**Jom Kokeattrakool**")
            st.divider()
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            if st.button("Sign Out", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

# แสดงสถานะเล็กๆ มุมขวา
st.markdown(f'<div class="top-nav"><div class="status-dot"></div><span style="font-size:0.6rem; color:var(--gold);">ONLINE</span></div>', unsafe_allow_html=True)

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
subtitle = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

st.divider()

# Upload Section
up_c1, up_c2 = st.columns(2)
with up_c1:
    st.markdown(f"<p style='text-align:center; font-size:0.8rem; font-weight:bold;'>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</p>", unsafe_allow_html=True)
    f_plan = st.file_uploader("up_plan", label_visibility="collapsed", type=['jpg','png','pdf'])
    if f_plan:
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        if f_plan.type != "application/pdf":
            st.image(f_plan, width=180)
        else:
            st.info("PDF Uploaded")
        st.markdown('</div>', unsafe_allow_html=True)

with up_c2:
    st.markdown(f"<p style='text-align:center; font-size:0.8rem; font-weight:bold;'>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</p>", unsafe_allow_html=True)
    f_site = st.file_uploader("up_site", label_visibility="collapsed", type=['jpg','png'])
    if f_site:
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        st.image(f_site, width=180)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Run Button
_, btn_space, _ = st.columns([1.3, 1, 1.3])
with btn_space:
    run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
    if st.button(run_txt, use_container_width=True, type="primary"):
        if f_plan or f_site:
            with st.spinner("Processing..."):
                time.sleep(1.5)
                st.success("Analysis Complete")
                st.markdown("---")
                st.markdown("**🔍 ANALYSIS SUMMARY**")
                st.write("ระบบตรวจพบความพร้อมของงานเหล็กเสริมพื้น (Rebar) เรียบร้อยแล้ว")
        else:
            st.warning("Please upload a file.")

st.markdown(f"<div style='text-align:center; margin-top:100px; color:#333; font-size:0.65rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
