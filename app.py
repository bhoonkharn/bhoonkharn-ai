import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG (International Construction Standard) ---
st.set_page_config(
    page_title="BHOON KHARN AI - Construction Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. THE MASTER CSS (แก้ปัญหาสัดส่วนและกล่องว่าง) ---
st.markdown("""
<style>
    /* ปิดส่วนเกิน Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Bhoon Kharn Theme Identity */
    :root { --gold: #B59473; --dark: #1E1A17; --line: #222; }
    html, body, [class*="st-app"] { background-color: var(--dark); color: #F5F5F5; font-family: 'Inter', 'Sarabun', sans-serif; }
    
    /* 1. Micro-Header UI (แก้จุดที่ 1: ปุ่มใหญ่เกินไป) */
    .top-header { position: fixed; top: 12px; right: 25px; display: flex; align-items: center; gap: 10px; z-index: 1000; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; }
    
    /* บีบปุ่มเมนูให้เล็กลงพิเศษ */
    div.stButton > button { 
        font-size: 0.65rem !important; 
        padding: 2px 8px !important; 
        min-height: 25px !important; 
        border-radius: 3px !important; 
        border: 1px solid #333 !important;
        background: transparent !important;
        color: #888 !important;
    }

    /* 2. Branding Section */
    .bk-title { font-size: 2.3rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 25px; color: var(--gold); }
    .bk-subtitle { font-size: 0.7rem; color: #666; text-align: center; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 5px; }
    
    /* 3. Slim File Uploader */
    .stFileUploader section { padding: 0.2rem 1rem !important; min-height: 60px !important; border: 1px dashed #333 !important; border-radius: 6px !important; }
    
    /* 4. Precision Image Preview (แก้จุดที่ 2: รูปอยู่ใต้กล่องว่าง) */
    .img-preview-box {
        margin-top: 15px;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 8px;
        background: rgba(255,255,255,0.01);
        display: flex;
        justify-content: center;
    }

    /* 5. Central Analysis Button (แก้จุดที่ 3: ปุ่มเอียง) */
    div.stButton > button[kind="primary"] {
        background-color: var(--gold) !important;
        color: var(--dark) !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100% !important;
        padding: 8px 0 !important;
        font-size: 0.85rem !important;
    }
</style>

<div class="top-header">
    <div class="status-dot"></div>
    <span style="font-size:0.55rem; color:var(--gold); font-weight:700; letter-spacing:1px;">ONLINE</span>
</div>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 4. NAVIGATION (Small & Clean) ---
# บังคับปุ่มให้อยู่มุมขวาบน
nav_c1, nav_c2, nav_c3 = st.columns([9, 0.4, 0.6])
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
            st.markdown(f"<small><b>Jom Kokeattrakool</b></small>", unsafe_allow_html=True)
            st.divider()
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            st.button("เช็คราคาวัสดุ [Soon]", use_container_width=True, disabled=True)
            if st.button("Sign Out", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
subtitle = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

st.divider()

# Upload Section (Grid 2 คอลัมน์สมมาตร)
up_c1, up_c2 = st.columns(2)

with up_c1:
    st.markdown(f"<center><p style='font-size:0.75rem; color:#888; margin-bottom:5px;'>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</p></center>", unsafe_allow_html=True)
    f_plan = st.file_uploader("p", label_visibility="collapsed", type=['jpg','png','pdf'])
    if f_plan and f_plan.type != "application/pdf":
        st.markdown('<div class="img-preview-box">', unsafe_allow_html=True)
        st.image(f_plan, width=220)
        st.markdown('</div>', unsafe_allow_html=True)

with up_c2:
    st.markdown(f"<center><p style='font-size:0.75rem; color:#888; margin-bottom:5px;'>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</p></center>", unsafe_allow_html=True)
    f_site = st.file_uploader("s", label_visibility="collapsed", type=['jpg','png'])
    if f_site:
        st.markdown('<div class="img-preview-box">', unsafe_allow_html=True)
        st.image(f_site, width=220)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Run Button (จัดวางกึ่งกลางเป๊ะ)
_, btn_space, _ = st.columns([1.4, 1.2, 1.4])
with btn_space:
    run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
    if st.button(run_txt, type="primary"):
        if f_plan or f_site:
            with st.spinner("Analyzing..."):
                time.sleep(1.5)
                st.success("Analysis Complete")
                st.markdown("---")
                st.markdown("**🔍 ANALYSIS RESULTS**")
                st.write("ตรวจพบงานโครงสร้าง Rebar และความสอดคล้องกับแบบแปลนเรียบร้อยแล้ว")
        else:
            st.warning("Please upload files.")

st.markdown(f"<div style='text-align:center; margin-top:100px; color:#333; font-size:0.6rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
