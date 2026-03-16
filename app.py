import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG (ลบความเป็น Streamlit ออกทั้งหมด) ---
st.set_page_config(
    page_title="BHOON KHARN AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. MASTER CSS (แก้ปัญหาสัดส่วน, Ghost Box และปุ่มเอียง) ---
st.markdown("""
<style>
    /* ปิดส่วนเกินของ Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    html, body, [class*="st-app"] { background-color: #1E1A17; color: #F5F5F5; font-family: 'Inter', sans-serif; }

    /* 1. ระบบ Header (ปุ่มจิ๋วและสถานะ) */
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 10px; z-index: 10000; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; margin-right: 5px; }
    
    div[data-testid="stColumn"] button {
        min-width: 45px !important; height: 28px !important;
        font-size: 0.65rem !important; padding: 0 !important;
        border: 1px solid #444 !important; background: transparent !important; color: #888 !important;
    }

    /* 2. กำจัดกล่องสี่เหลี่ยมเหนือรูป (Ghost Box Remover) */
    [data-testid="stFileUploaderFileName"], 
    [data-testid="stProgress"],
    .st-emotion-cache-12w0qpk, 
    .st-emotion-cache-not62 { display: none !important; }
    
    .stFileUploader section { 
        padding: 0.8rem 1rem !important; min-height: 80px !important; 
        border-radius: 6px !important; border: 1px solid #333 !important; 
        background: rgba(255,255,255,0.02) !important;
    }
    
    .preview-box {
        margin-top: 15px; text-align: center; border: 1px solid #333;
        border-radius: 8px; padding: 12px; background: rgba(0,0,0,0.15);
    }

    /* 3. ล็อกปุ่ม "เริ่มการวิเคราะห์" ให้อยู่กึ่งกลาง 100% (Flexbox Absolute Center) */
    .center-wrapper {
        display: flex; justify-content: center; align-items: center;
        width: 100%; margin: 40px 0;
    }
    div.stButton > button[kind="primary"] {
        background-color: #B59473 !important; color: #1E1A17 !important;
        width: 280px !important; height: 48px !important;
        border: none !important; font-weight: 700 !important; font-size: 0.95rem !important;
        border-radius: 6px !important;
    }

    /* Branding */
    .bk-title { font-size: 2.6rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 40px; color: #B59473; }
    .bk-subtitle { font-size: 0.75rem; color: #666; text-align: center; margin-bottom: 40px; text-transform: uppercase; letter-spacing: 5px; }
</style>

<div class="top-nav">
    <div class="status-dot"></div>
    <span style="font-size:0.55rem; color:#B59473; font-weight:700; letter-spacing:1px;">ONLINE</span>
</div>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (Persistent Memory) ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# ระบบ Buffer เก็บรูปไม่ให้หายตอน Rerun
if "img_plan" not in st.session_state: st.session_state.img_plan = None
if "img_site" not in st.session_state: st.session_state.img_site = None

# --- 4. NAVIGATION BAR ---
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
            # เมนู Vision ครบถ้วน
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            st.button("เช็คราคาวัสดุ [Coming Soon]", use_container_width=True, disabled=True)
            st.button("สร้างรายงาน PDF", use_container_width=True)
            if st.button("Sign Out", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
txt_sub = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{txt_sub}</div>", unsafe_allow_html=True)

st.divider()

# Grid Layout สำหรับอัปโหลด
up_col1, up_col2 = st.columns(2)

with up_col1:
    st.markdown(f"<center><b style='font-size:0.8rem;'>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</b></center>", unsafe_allow_html=True)
    f_plan = st.file_uploader("p", label_visibility="collapsed", type=['jpg','png','pdf'], key="uploader_p")
    
    # อัปเดต Buffer เมื่อมีการเปลี่ยนแปลง
    if f_plan: st.session_state.img_plan = f_plan
    elif not f_plan: st.session_state.img_plan = None
    
    if st.session_state.img_plan and st.session_state.img_plan.type != "application/pdf":
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(st.session_state.img_plan, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

with up_col2:
    st.markdown(f"<center><b style='font-size:0.8rem;'>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</b></center>", unsafe_allow_html=True)
    f_site = st.file_uploader("s", label_visibility="collapsed", type=['jpg','png'], key="uploader_s")
    
    if f_site: st.session_state.img_site = f_site
    elif not f_site: st.session_state.img_site = None
    
    if st.session_state.img_site:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(st.session_state.img_site, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. ACTION BUTTON (กึ่งกลางเป๊ะ 100%) ---
st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
if st.button(run_txt, type="primary"):
    if st.session_state.img_plan or st.session_state.img_site:
        with st.spinner("Analyzing..."):
            time.sleep(1.5)
            st.success("Complete")
    else:
        st.warning("Please upload files.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; margin-top:100px; color:#333; font-size:0.6rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
