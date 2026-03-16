import streamlit as st

# --- 1. CONFIG (International Title) ---
st.set_page_config(
    page_title="BHOON KHARN AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM CSS (Minimalist Style) ---
st.markdown("""
<style>
    /* ปิดแถบเมนูซ้ายและปุ่ม Sidebar 100% */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* โทนสีขาว คลีน สไตล์อินเตอร์ */
    html, body, [class*="st-app"] { background-color: #FFFFFF; color: #1A1A1A; font-family: 'Inter', 'Sarabun', sans-serif; }
    
    /* ระบบไฟสถานะมุมขวาบน */
    .status-bar { position: fixed; top: 25px; right: 30px; display: flex; align-items: center; gap: 15px; z-index: 1000; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background-color: #28a745; box-shadow: 0 0 5px #28a745; }
    .status-text { font-size: 0.75rem; font-weight: 700; color: #666; letter-spacing: 1px; }
    
    /* Branding */
    .bk-title { font-size: 3rem; font-weight: 700; text-align: center; letter-spacing: -2px; margin-top: 80px; color: #1A1A1A; }
    .bk-subtitle { font-size: 0.85rem; color: #999; text-align: center; margin-bottom: 60px; text-transform: uppercase; letter-spacing: 4px; }
    
    /* จัดการช่อง Upload ให้ดูแพง */
    .stFileUploader { border: 1px solid #F0F0F0; border-radius: 8px; padding: 10px; }
</style>

<div class="status-bar">
    <div style="display: flex; align-items: center; gap: 5px;">
        <div class="dot"></div> <span class="status-text">ONLINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (Language & Login) ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 4. HEADER NAVIGATION ---
nav_left, nav_right = st.columns([8, 2])

with nav_right:
    col_lang, col_user = st.columns([1, 1.2])
    with col_lang:
        if st.button(f"🌐 {st.session_state.lang}"):
            st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
            st.rerun()
    with col_user:
        if not st.session_state.logged_in:
            if st.button("SIGN IN"):
                st.session_state.logged_in = True
                st.rerun()
        else:
            with st.popover("👤 JOM"):
                st.markdown("**Menu Tools**")
                st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
                st.button("เช็คราคาวัสดุ [Soon]", use_container_width=True, disabled=True)
                if st.button("Sign Out", type="primary", use_container_width=True):
                    st.session_state.logged_in = False
                    st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
txt_sub = "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision" if st.session_state.lang == "TH" else "Advanced Construction Intelligence"
st.markdown(f"<div class='bk-subtitle'>{txt_sub}</div>", unsafe_allow_html=True)

st.divider()

# Upload Section
up_cols = st.columns(2)
with up_cols[0]:
    st.markdown(f"**{'1. แปลน / Blueprint' if st.session_state.lang == 'TH' else '1. Blueprint / Plan'}**")
    st.file_uploader("up1", label_visibility="collapsed")
with up_cols[1]:
    st.markdown(f"**{'2. รูปถ่ายหน้างาน' if st.session_state.lang == 'TH' else '2. Site Photo'}**")
    st.file_uploader("up2", label_visibility="collapsed")

st.markdown("<br><br>", unsafe_allow_html=True)

# Central Run Button
_, btn_space, _ = st.columns([1, 2, 1])
with btn_space:
    btn_text = "เริ่มการวิเคราะห์" if st.session_state.lang == "TH" else "RUN ANALYSIS"
    if st.button(btn_text, type="primary", use_container_width=True):
        st.toast("Analyzing project data...")

st.markdown(f"<div style='text-align:center; margin-top:150px; color:#DDD; font-size:0.7rem; letter-spacing:1px;'>© 2026 BHOON KHARN | INTERNATIONAL STANDARD</div>", unsafe_allow_html=True)
