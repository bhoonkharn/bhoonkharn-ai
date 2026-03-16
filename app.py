import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG (ลบความเป็น Streamlit 100%) ---
st.set_page_config(
    page_title="BHOON KHARN AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. MASTER CSS (Precision Tuning) ---
st.markdown("""
<style>
    /* ปิดส่วนเกิน */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Bhoon Kharn Theme */
    :root { --gold: #B59473; --dark: #1E1A17; }
    html, body, [class*="st-app"] { background-color: var(--dark); color: #F5F5F5; font-family: 'Inter', sans-serif; }

    /* Floating Top Nav (แก้ปัญหาปุ่มรวน) */
    .nav-container {
        position: fixed; top: 15px; right: 25px;
        display: flex; align-items: center; gap: 12px; z-index: 9999;
    }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #28a745; box-shadow: 0 0 6px #28a745; }
    
    /* Branding */
    .bk-title { font-size: 2.5rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 35px; color: var(--gold); }
    .bk-subtitle { font-size: 0.75rem; color: #666; text-align: center; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 5px; }
    
    /* Slim File Uploader */
    .stFileUploader section { padding: 0.2rem 1rem !important; min-height: 50px !important; border: 1px solid #333 !important; border-radius: 4px !important; }
    
    /* Image Preview (No Ghost Box) */
    .img-wrap { border: 1px solid #333; border-radius: 4px; padding: 10px; background: rgba(255,255,255,0.02); margin-top: 10px; text-align: center; }

    /* Central Button Fix */
    div.stButton > button[kind="primary"] {
        background-color: var(--gold) !important; color: var(--dark) !important;
        border: none !important; font-weight: 700 !important; width: 100% !important; border-radius: 4px !important;
    }
    
    /* Mini Buttons for Nav */
    .nav-container button {
        background: transparent !important; border: 1px solid #444 !important;
        color: #888 !important; font-size: 0.65rem !important; padding: 2px 10px !important; min-height: 25px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 4. FLOATING HEADER ---
# ส่วนนี้จะลอยอยู่ที่มุมขวาบนเสมอ ไม่ว่า Layout จะขยับยังไง
st.markdown(f"""
<div class="nav-container">
    <div style="display: flex; align-items: center; gap: 5px; margin-right: 10px;">
        <div class="status-dot"></div>
        <span style="font-size:0.6rem; color:var(--gold); font-weight:700;">ONLINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ใช้ปุ่มจริงเพื่อให้ Session State ทำงานได้
top_cols = st.columns([8.8, 0.4, 0.8])
with top_cols[1]:
    if st.button(st.session_state.lang):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with top_cols[2]:
    if not st.session_state.logged_in:
        if st.button("SIGN IN"):
            st.session_state.logged_in = True
            st.rerun()
    else:
        with st.popover("👤"):
            st.markdown(f"<small><b>คุณ {st.session_state.get('user_name', 'Nhum')}</b></small>", unsafe_allow_html=True)
            st.divider()
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            if st.button("Sign Out", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
subtitle = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

st.divider()

# Upload Section
up_c1, up_c2 = st.columns(2)

with up_c1:
    st.markdown(f"<center><small>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</small></center>", unsafe_allow_html=True)
    f_plan = st.file_uploader("p", label_visibility="collapsed", type=['jpg','png','pdf'])
    if f_plan and f_plan.type != "application/pdf":
        st.markdown('<div class="img-wrap">', unsafe_allow_html=True)
        st.image(f_plan, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

with up_c2:
    st.markdown(f"<center><small>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</small></center>", unsafe_allow_html=True)
    f_site = st.file_uploader("s", label_visibility="collapsed", type=['jpg','png'])
    if f_site:
        st.markdown('<div class="img-wrap">', unsafe_allow_html=True)
        st.image(f_site, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Analysis Section
_, btn_space, _ = st.columns([1.3, 1, 1.3])
with btn_space:
    run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
    if st.button(run_txt, type="primary"):
        if f_plan or f_site:
            with st.spinner("Analyzing..."):
                time.sleep(1.5)
                st.success("Complete")
                st.markdown("---")
                st.markdown("**🔍 ANALYSIS RESULTS**")
                st.write("ตรวจพบความสอดคล้องระหว่างงานหน้างานและแบบแปลน")
        else:
            st.warning("Please upload files.")

st.markdown(f"<div style='text-align:center; margin-top:100px; color:#333; font-size:0.6rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
