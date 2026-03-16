import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG ---
st.set_page_config(
    page_title="BHOON KHARN AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. MASTER CSS (Fixing All UI Glitches) ---
st.markdown("""
<style>
    /* ปิดส่วนเกินและล็อกพื้นหลัง */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    html, body, [class*="st-app"] { background-color: #1E1A17; color: #F5F5F5; font-family: 'Inter', sans-serif; }

    /* 1. แก้ไข Header ให้คงที่ (ปุ่มภาษาไม่ตกบรรทัด) */
    .nav-zone {
        position: fixed; top: 15px; right: 25px;
        display: flex; align-items: center; gap: 10px; z-index: 10000;
    }
    .stButton button {
        min-width: 45px !important; /* ล็อกความกว้างปุ่มไม่ให้ตกบรรทัด */
        height: 30px !important;
        font-size: 0.7rem !important;
        padding: 0 !important;
        border: 1px solid #444 !important;
        background: transparent !important;
        color: #888 !important;
    }

    /* 2. แก้ปัญหารูปพรีวิว (ลบกล่องว่าง) */
    .stFileUploader section { padding: 0.3rem 1rem !important; min-height: 50px !important; border-radius: 4px !important; }
    /* ซ่อนสถานะอัปโหลดสำเร็จของ Streamlit ที่ชอบขึ้นมาเป็นกล่องขาวๆ */
    [data-testid="stFileUploaderFileName"], .st-emotion-cache-12w0qpk { display: none !important; }
    
    .preview-box {
        margin-top: 10px;
        text-align: center;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 10px;
        background: rgba(255,255,255,0.02);
    }

    /* 3. ล็อกปุ่มวิเคราะห์ให้อยู่กึ่งกลางเป๊ะ */
    .center-btn-container {
        display: flex;
        justify-content: center;
        padding-top: 30px;
        width: 100%;
    }
    div.stButton > button[kind="primary"] {
        background-color: #B59473 !important;
        color: #1E1A17 !important;
        width: 280px !important; /* ล็อกขนาดปุ่มให้สมส่วน */
        border: none !important;
        font-weight: 700 !important;
        height: 45px !important;
    }

    /* Branding */
    .bk-title { font-size: 2.5rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 40px; color: #B59473; }
    .bk-subtitle { font-size: 0.75rem; color: #666; text-align: center; margin-bottom: 40px; text-transform: uppercase; letter-spacing: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 4. NAVIGATION (Floating UI) ---
# ใช้ Markdown สร้างโครงสร้างเพื่อให้ปุ่มเข้าที่
st.markdown(f"""
<div class="nav-zone">
    <div style="display: flex; align-items: center; gap: 5px; margin-right: 5px;">
        <div style="width:6px; height:6px; background:#28a745; border-radius:50%;"></div>
        <span style="font-size:0.6rem; color:#B59473; font-weight:700;">ONLINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# วางปุ่มจริงทับตำแหน่งที่ต้องการ (ใช้ columns บีบให้อยู่ขวา)
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
            st.markdown(f"**{st.session_state.get('user', 'JOM')}**")
            st.divider()
            if st.button("Sign Out", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
sub = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{sub}</div>", unsafe_allow_html=True)

st.divider()

# Grid Layout (2 คอลัมน์สมมาตร)
up_c1, up_c2 = st.columns(2)

with up_c1:
    st.markdown(f"<p style='text-align:center; font-size:0.8rem; font-weight:bold; color:#888;'>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</p>", unsafe_allow_html=True)
    f_plan = st.file_uploader("p", label_visibility="collapsed", type=['jpg','png','pdf'])
    if f_plan and f_plan.type != "application/pdf":
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(f_plan, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

with up_c2:
    st.markdown(f"<p style='text-align:center; font-size:0.8rem; font-weight:bold; color:#888;'>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</p>", unsafe_allow_html=True)
    f_site = st.file_uploader("s", label_visibility="collapsed", type=['jpg','png'])
    if f_site:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(f_site, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

# ส่วนปุ่มวิเคราะห์ (Center)
st.markdown("<div class='center-btn-container'>", unsafe_allow_html=True)
run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
if st.button(run_txt, type="primary"):
    if f_plan or f_site:
        with st.spinner("Analyzing..."):
            time.sleep(1.5)
            st.success("Complete")
    else:
        st.warning("Please upload files.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; margin-top:120px; color:#333; font-size:0.6rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
