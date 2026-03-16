import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import base64
from streamlit_oauth import OAuth2Component

# --- 1. CONFIG & BRANDING ---
st.set_page_config(
    page_title="BHOON KHARN AI", 
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; }
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-top: 10px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px; }
    .section-header { color: var(--bk-gold); font-size: 1.1rem; font-weight: 700; margin-top: 25px; margin-bottom: 10px; text-transform: uppercase; border-bottom: 1px solid rgba(181, 148, 115, 0.2); padding-bottom: 5px; }
    .content-list { line-height: 1.8; color: #E0E0E0; list-style-type: none; padding-left: 0; }
    .content-list li { margin-bottom: 8px; padding-left: 15px; border-left: 2px solid var(--bk-gold); }
    .next-task-box { background: rgba(181, 148, 115, 0.05); border: 1px solid var(--bk-gold); border-radius: 4px; padding: 15px; color: #F5F5F5; }
    .owner-box { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.03); margin: 20px 0; }
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 15px; z-index: 10000; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; margin-right: 5px; }
    .status-text { font-size: 0.65rem; color: #B59473; font-weight: 700; letter-spacing: 1px; }
    .mat-link { color: var(--bk-gold); text-decoration: none; font-weight: 700; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 🛑 ระบบ LOGIN (Google OAuth2) - คืนค่าตาม Success Case เป๊ะ 100%
# ==========================================================
CLIENT_ID = "358673361686-q6nuqn6tqefffcrm9krtcv1u11rmvt8j.apps.googleusercontent.com"
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
ADMIN_EMAIL = "bhoonkharn@gmail.com"

# แก้ไขจุดนี้: ใช้แค่ 5 ตัวแปรตามที่คุณเคยใช้ได้ (ตัด REVOKE_ENDPOINT ออก)
oauth2 = OAuth2Component(
    CLIENT_ID, 
    CLIENT_SECRET, 
    "https://accounts.google.com/o/oauth2/v2/auth", 
    "https://oauth2.googleapis.com/token", 
    "https://oauth2.googleapis.com/token"
)

if "auth" not in st.session_state:
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#A09080; letter-spacing:3px;'>PRIVATE SYSTEM ACCESS</p>", unsafe_allow_html=True)
    l_c1, l_c2, l_c3 = st.columns([1.2, 1, 1.2])
    with l_c2:
        # ระบุชื่อตัวแปรให้ชัดเจนตามที่คุณเคยแก้แล้วใช้ได้
        res = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.iconpacks.net/icons/2/free-google-icon-2039-thumb.png",
            redirect_uri="https://bhoonkharn-ai.streamlit.app", 
            scope="openid email profile",
            key="google_login",
            extras_params={"prompt": "select_account"}
        )
    if res:
        st.session_state["auth"] = res["token"]
        st.rerun()
    st.stop()

if "user_info" not in st.session_state:
    payload = st.session_state["auth"]["id_token"].split(".")[1]
    payload += "=" * ((4 - len(payload) % 4) % 4)
    st.session_state["user_info"] = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))

# ==========================================================
# 🟢 ระบบจัดการ MODEL (DYNAMIC MODEL HUNTER) 🟢
# ==========================================================
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

def init_ai_engine():
    try:
        genai.configure(api_key=API_KEY)
        available = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()]
        def sort_key(name):
            v = float(re.search(r'(\d+\.\d+)', name).group(1)) if re.search(r'(\d+\.\d+)', name) else 0.0
            tier = 0 if 'flash' in name else (1 if 'pro' in name else 2)
            return (v, -tier)
        available.sort(key=sort_key, reverse=True)
        email = st.session_state["user_info"].get("email", "")
        models_to_try = available if (email == ADMIN_EMAIL or st.session_state.usage_count == 0) else available[::-1]
        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(m_name)
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, f"ONLINE ({m_name})"
            except: continue
        return None, "OFFLINE"
    except: return None, "OFFLINE"

st.session_state.engine, st.session_state.status = init_ai_engine()

# ==========================================================
# 🏗️ HEADER & NAVIGATION 🏗️
# ==========================================================
st.markdown(f'<div class="top-nav"><div style="display:flex;align-items:center;"><div class="status-dot"></div><span class="status-text">{st.session_state.status}</span></div></div>', unsafe_allow_html=True)
nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang, key="lang_btn"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    user_name = st.session_state["user_info"].get("name", "USER").upper()
    with st.popover("👤"):
        st.markdown(f"**คุณ {user_name}**")
        st.divider()
        st.caption("TOOLS")
        st.button("ถอดแบบประเมินวัสดุ (SMART BOQ) [Coming Soon]", use_container_width=True, disabled=True)
        st.button("เช็คราคาวัสดุ 5 ห้างหลัก [Coming Soon]", use_container_width=True, disabled=True)
        st.button("แจ้งเตือนสภาพอากาศคิวเทปูน [Coming Soon]", use_container_width=True, disabled=True)
        st.divider()
        st.button("สร้างรายงาน PDF (TH/EN) [Upgrade to Pro]", use_container_width=True)
        if st.button("SIGN OUT", type="primary", use_container_width=True):
            del st.session_state["auth"]
            st.rerun()

# ==========================================================
# 📸 MAIN INTERFACE 📸
# ==========================================================
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>Construction Inspection Intelligence</div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>BLUEPRINT / แปลน</p>", unsafe_allow_html=True)
    bp = st.file_uploader("BP", type=['jpg','jpeg','png','pdf'], label_visibility="collapsed")
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>SITE PHOTO / หน้างาน</p>", unsafe_allow_html=True)
    site = st.file_uploader("SITE", type=['jpg','jpeg','png'], label_visibility="collapsed")
    if site: st.image(site)

if st.button("RUN ANALYSIS / เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site:
        if not st.session_state.engine: st.error("Engine Offline")
        else:
            with st.spinner("ANALYZING..."):
                try:
                    prompt = 'วิเคราะห์ภาพและตอบเป็น JSON ภาษาไทย: {"analysis":[], "risk":[], "checklist":[], "standard":[], "next_task":"", "materials":[], "owner_note":[]}'
                    img_inp = Image.open(site) if site else Image.open(bp)
                    res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
                    st.session_state.json_data = json.loads(res.text)
                    st.session_state.usage_count += 1
                except Exception as e: st.error(f"Error: {e}")
    else: st.warning("Please upload image")

# ==========================================================
# 📊 RESULTS DISPLAY 📊
# ==========================================================
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
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
        st.markdown(f"<div class='next-task-box'><b>{d['next_task']}</b></div>", unsafe_allow_html=True)
    if "materials" in d:
        st.markdown("<div class='section-header'>🗓️ รายการวัสดุที่ต้องเตรียม</div>", unsafe_allow_html=True)
        for item in d["materials"][:7]:
            url = f"https://www.google.com/search?q={item}"
            st.markdown(f"• <a href='{url}' target='_blank' class='mat-link'>{item}</a>", unsafe_allow_html=True)
    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 คำแนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        html = "<div class='owner-box'><ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in d["owner_note"]]) + "</ul></div>"
        st.markdown(html, unsafe_allow_html=True)
st.markdown("<div style='text-align:center; margin-top:50px; color:#4A3F35; font-size:0.7rem;'>BHOON KHARN | PRIVATE SYSTEM</div>", unsafe_allow_html=True)
