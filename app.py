import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# --- 5. หน้าตาเว็บ (Minimalist SRS Phase 1) ---
st.set_page_config(
    page_title="BHOON KHARN AI", 
    page_icon="logo.png", # ใช้ไอคอนบน Tab Browser เท่านั้น
    layout="wide",
    initial_sidebar_state="collapsed"
)

# สไตล์ Minimalist (Gold/Dark Theme) ตามสั่ง ไม่ใช้ Emoji
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; }
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-top: 10px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; letter-spacing: 2px; }
    
    .section-header { color: var(--bk-gold); font-size: 1.1rem; font-weight: 700; margin-top: 25px; margin-bottom: 10px; border-bottom: 1px solid rgba(181, 148, 115, 0.2); padding-bottom: 5px; }
    .content-list { line-height: 1.8; color: #E0E0E0; list-style-type: none; padding-left: 0; }
    .content-list li { margin-bottom: 8px; padding-left: 15px; border-left: 2px solid var(--bk-gold); }
    
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 15px; z-index: 10000; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; margin-right: 5px; }
    .status-text { font-size: 0.65rem; color: #B59473; font-weight: 700; letter-spacing: 1px; }
    .mat-link { color: var(--bk-gold); text-decoration: none; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# Initial State
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}
if "is_admin" not in st.session_state: st.session_state.is_admin = True # จำลองสถานะ Admin เพื่อเทส

# --- 2. ระบบค้นหา Model อัจฉริยะ (Dynamic Model Hunter) ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

def init_ai_engine():
    try:
        genai.configure(api_key=API_KEY)
        
        # ดึงรายชื่อ Model อัตโนมัติ (No Hardcode)
        try:
            available_models = [m.name.replace("models/", "") for m in genai.list_models() 
                              if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()]
        except:
            # สำรองรุ่นพื้นฐานหากดึงรายชื่อไม่ได้
            available_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
        
        # จัดเรียง (ใหม่ไปเก่า)
        def sort_logic(name):
            v_match = re.search(r'(\d+\.\d+)', name)
            v = float(v_match.group(1)) if v_match else 1.0
            tier = 0 if 'flash' in name else (1 if 'pro' in name else 2)
            return (v, -tier)
        available_models.sort(key=sort_logic, reverse=True)

        # 1. Privilege Logic (Admin vs General)
        if st.session_state.is_admin or st.session_state.usage_count == 0:
            target_list = available_models # Admin/ครั้งแรก: ลองจากรุ่นใหม่สุด
        else:
            target_list = available_models[::-1] # ครั้งถัดไป: ลองจากรุ่นเก่าสุดเพื่อประหยัด

        # Loop & Try: วนทดสอบจนกว่าจะเจอตัวที่ Online จริง
        for m_name in target_list:
            try:
                m = genai.GenerativeModel(m_name)
                # ทดสอบเบาๆ เพื่อเช็คสิทธิ์ใช้งานจริง
                m.generate_content("test", generation_config={"max_output_tokens": 1})
                return m, f"ONLINE ({m_name})"
            except:
                continue
        return None, "OFFLINE"
    except:
        return None, "OFFLINE (CONNECTION ERROR)"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# --- 5. Header: มุมขวาบน (ไฟสถานะ, สลับภาษา, Popover) ---
st.markdown(f'<div class="top-nav"><div style="display:flex;align-items:center;"><div class="status-dot"></div><span class="status-text">{st.session_state.status}</span></div></div>', unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    with st.popover("👤"):
        # --- 3. เมนูเครื่องมือใน Popover (Full Menu Structure) ---
        st.markdown(f"**STATUS: {'ADMIN' if st.session_state.is_admin else 'GENERAL'}**")
        if st.button("สลับสิทธิ์ (ทดสอบระบบวน Model)"):
            st.session_state.is_admin = not st.session_state.is_admin
            st.session_state.engine, st.session_state.status = init_ai_engine()
            st.rerun()
        st.divider()
        st.caption("TOOLS")
        st.button("ถอดแบบประเมินวัสดุ (Smart BOQ) [Coming Soon]", use_container_width=True, disabled=True)
        st.button("เช็คราคาวัสดุ 5 ห้างหลัก [Coming Soon]", use_container_width=True, disabled=True)
        st.button("แจ้งเตือนสภาพอากาศคิวเทปูน [Coming Soon]", use_container_width=True, disabled=True)
        st.divider()
        st.button("สร้างรายงาน PDF (TH/EN) [Upgrade to Pro]", use_container_width=True)
        st.button("ออกจากระบบ (Sign Out)", type="primary", use_container_width=True)

# --- 📸 MAIN INTERFACE ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>Construction Inspection Intelligence</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>BLUEPRINT / แปลน</p>", unsafe_allow_html=True)
    bp = st.file_uploader("BP_UPLOAD", type=['jpg','jpeg','png','pdf'], label_visibility="collapsed")
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>SITE PHOTO / หน้างาน</p>", unsafe_allow_html=True)
    site = st.file_uploader("SITE_UPLOAD", type=['jpg','jpeg','png'], label_visibility="collapsed")
    if site: st.image(site)

if st.button("RUN ANALYSIS / เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site:
        if not st.session_state.engine:
            st.session_state.engine, st.session_state.status = init_ai_engine()
            st.rerun()
        else:
            with st.spinner("ANALYZING..."):
                try:
                    prompt = 'วิเคราะห์ภาพเปรียบเทียบและตอบเป็น JSON ภาษาไทย: {"analysis":[], "risk":[], "checklist":[], "standard":[], "next_task":"", "materials":[], "owner_note":[]}'
                    img_inp = Image.open(site) if site else Image.open(bp)
                    res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
                    st.session_state.json_data = json.loads(res.text)
                    st.session_state.usage_count += 1
                except Exception as e: st.error(f"Error during analysis: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 4. การแสดงผลวิเคราะห์และวัสดุ (Results & Search Links) ---
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
    
    # Minimalist Results: ข้อๆ ตัวหนา เส้นแบ่ง ไม่ใช้ไอคอน
    def render_sec(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            items = d[key]
            if isinstance(items, list):
                html = "<ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in items]) + "</ul>"
                st.markdown(html, unsafe_allow_html=True)
            else: st.markdown(f"<div style='margin-bottom:20px;'><b>{items}</b></div>", unsafe_allow_html=True)

    render_sec("🔍 วิเคราะห์หน้างาน", "analysis")
    render_sec("⚠️ จุดวิกฤตที่ต้องระวัง", "risk")
    render_sec("📝 เทคนิคการตรวจงาน", "checklist")
    render_sec("🏗️ มาตรฐานวิศวกรรม", "standard")
    
    if "next_task" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไป</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom:20px;'><b>{d['next_task']}</b></div>", unsafe_allow_html=True)

    # Material Search List: 5-7 รายการ ลิงก์ไป Google Search (Text Only)
    if "materials" in d:
        st.markdown("<div class='section-header'>🗓️ รายการวัสดุที่ต้องเตรียม</div>", unsafe_allow_html=True)
        for item in d["materials"][:7]:
            url = f"https://www.google.com/search?q={item}"
            st.markdown(f"• <a href='{url}' target='_blank' class='mat-link'>{item}</a>", unsafe_allow_html=True)

    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 คำแนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        html = "<ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in d["owner_note"]]) + "</ul>"
        st.markdown(html, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; margin-top:50px; color:#4A3F35; font-size:0.7rem;'>BHOON KHARN | PRIVATE SYSTEM</div>", unsafe_allow_html=True)
