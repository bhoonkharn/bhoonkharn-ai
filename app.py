import streamlit as st
from PIL import Image
import time

# --- 1. CONFIG (ฝังคำสั่งลบ Streamlit ออกจาก Title และใช้โลโก้) ---
st.set_page_config(
    page_title="BHOON KHARN - Construction AI Platform",
    page_icon="🏗️", # ในอนาคตเปลี่ยนเป็น "logo.png"
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CSS (Identity & Proportional UI) ---
st.markdown("""
<style>
    /* ปิด Sidebar และส่วนที่ไม่จำเป็น 100% */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Bhoon Kharn Theme */
    :root { --gold: #B59473; --dark: #1E1A17; --brown: #4A3F35; }
    html, body, [class*="st-app"] { background-color: var(--dark); color: #F5F5F5; font-family: 'Inter', 'Sarabun', sans-serif; }
    
    /* Header & Status (Small & Clean) */
    .top-nav { position: fixed; top: 15px; right: 30px; display: flex; align-items: center; gap: 15px; z-index: 999; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; display: inline-block; }
    .status-lbl { font-size: 0.65rem; font-weight: 700; color: var(--gold); letter-spacing: 1px; margin-right: 15px; }

    /* Branding Section */
    .bk-title { font-size: 2.5rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin-top: 40px; color: var(--gold); }
    .bk-subtitle { font-size: 0.8rem; color: #888; text-align: center; margin-bottom: 35px; text-transform: uppercase; letter-spacing: 4px; }
    
    /* บีบช่อง Upload ให้เล็กลง (Proportional Fix) */
    .stFileUploader { max-width: 450px; margin: 0 auto; }
    .stFileUploader section { padding: 0.2rem 1rem !important; min-height: 80px !important; }
    .stFileUploader label { display: none; } /* ซ่อน Label เดิมเพื่อประหยัดที่ */
    
    /* ปุ่มวิเคราะห์สีทองสไตล์หรู */
    div.stButton > button {
        background-color: var(--gold) !important;
        color: var(--dark) !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        padding: 0.5rem 2rem !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(181, 148, 115, 0.4); }

    /* ปรับแต่ง Dropdown & Popover */
    .stPopover button { background: transparent !important; border: 1px solid #333 !important; color: white !important; padding: 4px 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 4. TOP NAVIGATION (Minimalist Status, Lang, Login) ---
st.markdown(f'<div class="top-nav"><div class="status-dot"></div><span class="status-lbl">ONLINE</span></div>', unsafe_allow_html=True)

nav_cols = st.columns([8.5, 0.7, 0.8])
with nav_cols[1]:
    # ปุ่มเปลี่ยนภาษาขนาดเล็ก
    if st.button(st.session_state.lang, key="lang_btn"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()

with nav_cols[2]:
    if not st.session_state.logged_in:
        if st.button("SIGN IN", key="login_btn"):
            st.session_state.logged_in = True
            st.rerun()
    else:
        # ล็อกอินสำเร็จ เปลี่ยนเป็นรูปโปรไฟล์ขนาดเล็ก + Dropdown
        with st.popover("👤"):
            st.markdown(f"**Jom Kokeattrakool**")
            st.caption("Standard Plan")
            st.divider()
            st.button("ถอดแบบ BOQ [Pro]", use_container_width=True, disabled=True)
            st.button("เช็คราคาวัสดุ [Coming Soon]", use_container_width=True, disabled=True)
            st.button("สร้างรายงาน PDF", use_container_width=True)
            if st.button("Sign Out", type="primary", use_container_width=True):
                st.session_state.is_logged_in = False
                st.session_state.logged_in = False
                st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
subtitle = "Advanced Construction Intelligence" if st.session_state.lang == "EN" else "วิเคราะห์หน้างานก่อสร้างด้วย AI Vision"
st.markdown(f"<div class='bk-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

st.markdown("---")

# ส่วน Upload แบบบีบสัดส่วน
up_c1, up_c2 = st.columns(2)
with up_c1:
    st.markdown(f"<center><b>{'BLUEPRINT / PLAN' if st.session_state.lang == 'EN' else 'แปลน / Blueprint'}</b></center>", unsafe_allow_html=True)
    f_plan = st.file_uploader("up_plan", label_visibility="collapsed", type=['jpg','png','pdf'])
    if f_plan and f_plan.type != "application/pdf":
        st.image(f_plan, width=120)

with up_c2:
    st.markdown(f"<center><b>{'SITE PHOTO' if st.session_state.lang == 'EN' else 'รูปถ่ายหน้างาน'}</b></center>", unsafe_allow_html=True)
    f_site = st.file_uploader("up_site", label_visibility="collapsed", type=['jpg','png'])
    if f_site:
        st.image(f_site, width=120)

st.markdown("<br>", unsafe_allow_html=True)

# ส่วน Run Analysis
_, run_btn_space, _ = st.columns([1.2, 1, 1.2])
with run_btn_space:
    run_txt = "RUN ANALYSIS" if st.session_state.lang == "EN" else "เริ่มการวิเคราะห์"
    if st.button(run_txt, use_container_width=True):
        if f_plan or f_site:
            with st.spinner("Processing..."):
                time.sleep(1.5)
                st.success("Analysis Complete" if st.session_state.lang == "EN" else "วิเคราะห์สำเร็จ")
                
                # ตัวอย่างการแสดงผลแบบไม่มีไอคอน รกๆ (ใช้แค่ตัวหนาและเส้นแบ่ง)
                st.markdown("---")
                st.markdown("**🔍 ANALYSIS SUMMARY**" if st.session_state.lang == "EN" else "**🔍 สรุปผลการวิเคราะห์**")
                st.write("ตรวจพบงานโครงสร้างเหล็กเสริม พื้นบริเวณชั้น 1 มีความพร้อมสำหรับการเทคอนกรีต")
                
                st.markdown("**🏗️ MATERIAL ESTIMATE**" if st.session_state.lang == "EN" else "**🏗️ รายการวัสดุที่เกี่ยวข้อง**")
                st.write("- คอนกรีตผสมเสร็จ 240 ksc")
                st.write("- เครื่องจี้คอนกรีต (Vibrator)")
        else:
            st.warning("Please upload a file first." if st.session_state.lang == "EN" else "กรุณาอัปโหลดรูปภาพ")

st.markdown(f"<div style='text-align:center; margin-top:120px; color:#444; font-size:0.7rem; letter-spacing:2px;'>BHOON KHARN © 2026 | INTERNATIONAL CONSTRUCTION STANDARD</div>", unsafe_allow_html=True)
