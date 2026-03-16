import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG (ล็อกชื่อแอปและโลโก้) ---
st.set_page_config(
    page_title="BHOON KHARN - Construction AI Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. MASTER CSS (เน้นความชัดเจนและตำแหน่งที่เป๊ะ) ---
st.markdown("""
<style>
    /* ปิดส่วนเกินของ Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    html, body, [class*="st-app"] { background-color: #1E1A17; color: #F5F5F5; font-family: 'Inter', sans-serif; }

    /* 1. ระบบ Header (ปุ่มภาษาและ Login เล็กสมส่วน) */
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 10px; z-index: 10000; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; margin-right: 5px; }
    
    /* ล็อกขนาดปุ่มเมนูมุมขวา */
    div[data-testid="stColumn"] button {
        min-width: 45px !important; height: 28px !important;
        font-size: 0.65rem !important; padding: 0 !important;
        border: 1px solid #444 !important; background: transparent !important; color: #888 !important;
    }

    /* 2. แก้ไขช่อง Upload (กลับไปใช้ขนาดมาตรฐานที่เห็นชัดเจน และโชว์ปุ่ม X) */
    .stFileUploader section { 
        padding: 1rem !important; 
        min-height: 100px !important; 
        border: 1px solid #333 !important; 
        border-radius: 8px !important; 
        background: rgba(255,255,255,0.02) !important;
    }
    /* คืนค่าปุ่ม X และชื่อไฟล์ให้เห็นชัดเจน */
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderDeleteBtn"] { 
        display: inline-flex !important; 
        color: #B59473 !important;
    }
    
    /* 3. ลบ "กล่องผี" สี่เหลี่ยมสีเหลือง/ขาว เหนือรูปพรีวิว */
    .stProgress, .st-emotion-cache-not62 { display: none !important; }

    /* 4. กรอบรูปพรีวิว (สมส่วนและอยู่ในแนวเส้น) */
    .preview-box {
        margin-top: 15px; text-align: center; border: 1px solid #333;
        border-radius: 8px; padding: 12px; background: rgba(0,0,0,0.2);
    }

    /* 5. ล็อกปุ่ม "เริ่มการวิเคราะห์" ให้อยู่กึ่งกลางเป๊ะ (Flexbox Center) */
    .center-container {
        display: flex; justify-content: center; width: 100%; margin: 40px 0;
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

# --- 3. SESSION STATE (จัดการข้อมูลให้คงอยู่แม้ Log in) ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

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
            # เรียกคืนหมวดงาน Vision ทั้งหมด
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

# Upload Section (คืนค่าขนาดที่มองเห็นชัดเจน)
up_col1, up_col2 = st.columns(2)

with up_col1:
    st.markdown(f"<center><b style='font-size:0.8rem;'>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</b></center>", unsafe_allow_html=True)
    # ใช้ Stable Key เพื่อให้รูปไม่หายตอนเปลี่ยนสถานะ Login
    f_plan = st.file_uploader("uploader_p", label_visibility="collapsed", type=['jpg','png','pdf'], key="file_p")
    if f_plan and f_plan.type != "application/pdf":
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(f_plan, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

with up_col2:
    st.markdown(f"<center><b style='font-size:0.8rem;'>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</b></center>", unsafe_allow_html=True)
    f_site = st.file_uploader("uploader_s", label_visibility="collapsed", type=['jpg','png'], key="file_s")
    if f_site:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(f_site, width=280)
        st.markdown('</div>', unsafe_allow_html=True)

# ส่วนปุ่มวิเคราะห์ (ล็อกกึ่งกลางด้วย CSS Container)
st.markdown("<div class='center-container'>", unsafe_allow_html=True)
run_label = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
if st.button(run_label, type="primary"):
    if f_plan or f_site:
        with st.spinner("AI is analyzing..."):
            time.sleep(1.5)
            st.success("Complete")
    else:
        st.warning("Please upload files.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; margin-top:100px; color:#333; font-size:0.6rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
