import streamlit as st
from PIL import Image
import os

# --- 1. CONFIG (ลบ Streamlit ออกจาก Title และใช้ Page Icon) ---
st.set_page_config(
    page_title="BHOON KHARN - Construction AI Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CSS (Precision Geometry) ---
st.markdown("""
<style>
    /* ปิดส่วนเกินของ Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Bhoon Kharn Theme Identity */
    :root { --gold: #B59473; --dark: #1E1A17; --line: #333; }
    html, body, [class*="st-app"] { background-color: var(--dark); color: #F5F5F5; font-family: 'Inter', 'Sarabun', sans-serif; }
    
    /* Slim Header (แก้จุดที่ 1: ปุ่มใหญ่เกินไป) */
    .header-zone { position: fixed; top: 10px; right: 20px; display: flex; align-items: center; gap: 8px; z-index: 1000; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #28a745; margin-right: 4px; }
    
    /* บีบขนาดปุ่มใน Header ให้เล็กจิ๋ว */
    .stButton button { font-size: 0.7rem !important; padding: 2px 10px !important; min-height: 28px !important; border-radius: 4px !important; border: 1px solid #444 !important; }

    /* Branding */
    .bk-title { font-size: 2.2rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 20px; color: var(--gold); }
    .bk-subtitle { font-size: 0.75rem; color: #777; text-align: center; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 4px; }
    
    /* Proportional File Uploader (แก้จุดที่ 2: ช่องอัปโหลด) */
    .stFileUploader section { padding: 0.2rem 1rem !important; min-height: 60px !important; border: 1px dashed var(--line) !important; border-radius: 8px !important; }
    
    /* Image Preview Frame (จัดรูปให้อยู่ในระนาบเดียวกับกรอบ) */
    .img-frame {
        display: flex; justify-content: center; align-items: center;
        border: 1px solid var(--line); border-radius: 8px;
        padding: 10px; background: rgba(255,255,255,0.02);
        margin-top: 15px; width: 100%; height: 200px;
    }
    .img-frame img { max-height: 100%; width: auto; border-radius: 4px; }
    
    /* ปุ่มวิเคราะห์สีทอง */
    div.stButton > button[kind="primary"] {
        background-color: var(--gold) !important; color: var(--dark) !important;
        border: none !important; font-weight: 700 !important; width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & SESSION STATE ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False

# --- 4. NAVIGATION BAR (Slim & Professional) ---
st.markdown('<div class="header-zone"><div class="status-dot"></div><span style="font-size:0.6rem; color:#B59473; font-weight:700;">ONLINE</span></div>', unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns([8.8, 0.5, 0.7])
with nav_c2:
    if st.button(st.session_state.lang):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    if not st.session_state.is_logged_in:
        if st.button("SIGN IN"):
            st.session_state.is_logged_in = True
            st.rerun()
    else:
        with st.popover("👤"):
            st.markdown(f"**คุณ {st.session_state.get('user_name', 'Nhum')}**")
            st.divider()
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            st.button("เช็คราคาวัสดุ [Soon]", use_container_width=True, disabled=True)
            if st.button("Sign Out", type="primary", use_container_width=True):
                st.session_state.is_logged_in = False
                st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
subtitle = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

st.divider()

# Grid Layout สำหรับอัปโหลดและพรีวิว
up_col1, up_col2 = st.columns(2)

with up_col1:
    st.markdown(f"<center><small>1. {'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</small></center>", unsafe_allow_html=True)
    f_plan = st.file_uploader("p", label_visibility="collapsed", type=['jpg','png','pdf'])
    if f_plan:
        if f_plan.type != "application/pdf":
            # ใส่รูปใน Container เพื่อจัดให้อยู่กึ่งกลาง
            st.markdown('<div class="img-frame">', unsafe_allow_html=True)
            st.image(f_plan, use_container_width=False, width=250)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("PDF File Uploaded")

with up_col2:
    st.markdown(f"<center><small>2. {'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</small></center>", unsafe_allow_html=True)
    f_site = st.file_uploader("s", label_visibility="collapsed", type=['jpg','png'])
    if f_site:
        st.markdown('<div class="img-frame">', unsafe_allow_html=True)
        st.image(f_site, use_container_width=False, width=250)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ส่วนวิเคราะห์ (พร้อมต่อยอดสู่ Phase 2)
_, btn_space, _ = st.columns([1.2, 1, 1.2])
with btn_space:
    run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
    if st.button(run_txt, type="primary"):
        if f_plan or f_site:
            with st.spinner("BHOON KHARN AI is processing..."):
                # จุดนี้คือที่ที่เราจะใส่เครื่องยนต์ Gemini เข้าไปใน Phase 2
                import time
                time.sleep(1.5)
                st.success("Analysis Completed")
                st.markdown("---")
                st.markdown("**🔍 ผลการวิเคราะห์**")
                st.info("AI ตรวจพบความสอดคล้องระหว่างแปลนและงานหน้างาน 95%")
        else:
            st.warning("Please upload files first.")

st.markdown(f"<div style='text-align:center; margin-top:120px; color:#333; font-size:0.6rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
