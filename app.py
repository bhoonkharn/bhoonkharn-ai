import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG (International Construction Platform) ---
st.set_page_config(
    page_title="BHOON KHARN AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. MASTER CSS (Fixing Ghost Boxes & Alignment) ---
st.markdown("""
<style>
    /* ปิดส่วนเกินของ Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    html, body, [class*="st-app"] { background-color: #1E1A17; color: #F5F5F5; font-family: 'Inter', sans-serif; }

    /* 1. แก้ไข Header (Navigation) */
    .nav-container {
        position: fixed; top: 15px; right: 25px;
        display: flex; align-items: center; gap: 10px; z-index: 10000;
    }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; }
    
    /* บีบขนาดปุ่มใน Nav ให้เล็กและนิ่ง */
    div[data-testid="stColumn"] button {
        min-width: 45px !important; height: 28px !important;
        font-size: 0.65rem !important; padding: 0 !important;
        border: 1px solid #444 !important; background: transparent !important; color: #888 !important;
    }

    /* 2. กำจัดกล่องสี่เหลี่ยมเหนือรูป (Ghost Boxes) */
    [data-testid="stFileUploaderFileName"], 
    [data-testid="stFileUploaderDeleteBtn"],
    .st-emotion-cache-12w0qpk, 
    .st-emotion-cache-not62 { display: none !important; }
    
    .stFileUploader section { padding: 0.2rem 1rem !important; min-height: 50px !important; border-radius: 4px !important; border: 1px solid #333 !important; }
    
    .preview-wrap {
        margin-top: 15px; text-align: center; border: 1px solid #333;
        border-radius: 6px; padding: 10px; background: rgba(255,255,255,0.01);
    }

    /* 3. ล็อกปุ่ม "เริ่มการวิเคราะห์" ให้อยู่กึ่งกลางเป๊ะ (Flexbox) */
    .center-action {
        display: flex; justify-content: center; align-items: center;
        width: 100%; margin-top: 40px; margin-bottom: 20px;
    }
    div.stButton > button[kind="primary"] {
        background-color: #B59473 !important; color: #1E1A17 !important;
        width: 260px !important; height: 45px !important;
        border: none !important; font-weight: 700 !important; font-size: 0.9rem !important;
        border-radius: 4px !important;
    }

    /* Branding */
    .bk-title { font-size: 2.4rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 40px; color: #B59473; }
    .bk-subtitle { font-size: 0.7rem; color: #666; text-align: center; margin-bottom: 40px; text-transform: uppercase; letter-spacing: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 4. FLOATING HEADER ---
st.markdown(f"""
<div class="nav-container">
    <div style="display: flex; align-items: center; gap: 5px; margin-right: 5px;">
        <div class="status-dot"></div>
        <span style="font-size:0.55rem; color:#B59473; font-weight:700; letter-spacing:1px;">ONLINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ปุ่มภาษาและ Login
nav_c1, nav_c2, nav_c3 = st.columns([9.1, 0.4, 0.5])
with nav_c2:
    if st.button(st.session_state.lang):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    if not st.session_state.logged_in:
        if st.button("SIGN IN"):
            st.session_state.logged_in = True
            st.rerun()
    else:
        with st.popover("👤"):
            st.markdown(f"**คุณ {st.session_state.get('user', 'JOM')}**")
            st.divider()
            # เรียกคืนหมวดงานที่ต้องมี
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            st.button("เช็คราคาวัสดุ [Coming Soon]", use_container_width=True, disabled=True)
            st.button("สร้างรายงาน PDF", use_container_width=True)
            if st.button("Sign Out", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
subtitle = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

st.divider()

# Grid Layout (2 คอลัมน์สมดุล)
up_c1, up_c2 = st.columns(2)

with up_c1:
    st.markdown(f"<center><p style='font-size:0.75rem; color:#888; font-weight:bold;'>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</p></center>", unsafe_allow_html=True)
    f_plan = st.file_uploader("up1", label_visibility="collapsed", type=['jpg','png','pdf'])
    if f_plan and f_plan.type != "application/pdf":
        st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
        st.image(f_plan, width=240)
        st.markdown('</div>', unsafe_allow_html=True)

with up_c2:
    st.markdown(f"<center><p style='font-size:0.75rem; color:#888; font-weight:bold;'>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</p></center>", unsafe_allow_html=True)
    f_site = st.file_uploader("up2", label_visibility="collapsed", type=['jpg','png'])
    if f_site:
        st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
        st.image(f_site, width=240)
        st.markdown('</div>', unsafe_allow_html=True)

# ส่วนปุ่มวิเคราะห์ (ล็อกกึ่งกลางด้วย Flexbox Container)
st.markdown("<div class='center-action'>", unsafe_allow_html=True)
run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
if st.button(run_txt, type="primary"):
    if f_plan or f_site:
        with st.spinner("AI is analyzing..."):
            time.sleep(1.5)
            st.success("Complete")
    else:
        st.warning("Please upload files.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; margin-top:100px; color:#333; font-size:0.6rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
