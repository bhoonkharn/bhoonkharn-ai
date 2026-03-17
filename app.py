import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import base64
import requests
from datetime import datetime
from streamlit_oauth import OAuth2Component

# --- 1. CONFIG & STYLE (UI 100% ตามพิมพ์เขียว) ---
st.set_page_config(
    page_title="BHOON KHARN AI", 
    page_icon="logo.png", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-dark: #1E1A17; }
    
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-top: 10px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; letter-spacing: 2px; border: none; background: transparent; }
    
    /* แก้ไขปุ่มเปลี่ยนภาษาให้ล็อคบรรทัดเดียว */
    div.stButton > button[key="lang_btn"] { 
        min-width: 90px !important; width: 90px !important; 
        white-space: nowrap !important; padding: 0px !important; height: 35px !important; 
    }

    button[kind="primary"] { 
        background-color: rgba(181, 148, 115, 0.1) !important; 
        color: var(--bk-gold) !important; border: 1px solid var(--bk-gold) !important;
        border-radius: 6px !important; font-weight: 700 !important; width: 100% !important;
    }
    button[kind="primary"]:hover { background-color: var(--bk-gold) !important; color: var(--bk-dark) !important; }

    /* การจัดระเบียบราคาวัสดุซ้าย-ขวา */
    .mat-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 10px 0; border-bottom: 1px solid rgba(181, 148, 115, 0.1); }
    .mat-link { color: var(--bk-gold); text-decoration: none; font-weight: 700; font-size: 1.05rem; }
    .mat-price { color: #28a745; font-size: 1rem; font-weight: 700; }
    
    .section-header { color: var(--bk-gold); font-size: 1.15rem; font-weight: 700; margin-top: 30px; margin-bottom: 15px; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 10px; }
    .content-list { line-height: 1.8; color: #E0E0E0; list-style-type: none; padding-left: 0; width: 100%; }
    .content-list li { margin-bottom: 12px; padding-left: 20px; border-left: 3px solid var(--bk-gold); display: block; }
    .owner-box { border-left: 4px solid var(--bk-gold); padding: 5px 20px; background: rgba(181, 148, 115, 0.05); margin: 20px 0; border-radius: 0 10px 10px 0; }
    .footer-box { text-align: center; margin-top: 40px; padding: 30px 0; border-top: 1px solid rgba(181, 148, 115, 0.1); }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIAL STATES & SECRETS ---
if "identified" not in st.session_state: st.session_state.identified = False
if "user_info" not in st.session_state: st.session_state.user_info = {}
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}

CLIENT_ID = "358673361686-q6nuqn6tqefffcrm9krtcv1u11rmvt8j.apps.googleusercontent.com"
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
GSHEET_URL = "https://script.google.com/macros/s/AKfycbzv0vktozJcK5B2BAvVM1yxrzBkUUUD2O1EL_Ex8cnK2MIPNWWvpP-My4YmVudVM2Se/exec"
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/v2/auth", "https://oauth2.googleapis.com/token", "https://oauth2.googleapis.com/token")

# ฟังก์ชันส่งข้อมูลเข้า Google Sheet
def sync_to_sheet(name, contact, type_user):
    try:
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "contact": contact,
            "status": type_user
        }
        requests.post(GSHEET_URL, data=json.dumps(data))
    except: pass

# --- 3. GATEKEEPER PAGE (ด่านระบุตัวตน) ---
if not st.session_state.identified:
    st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#A09080;'>กรุณาระบุตัวตนเพื่อเข้าใช้งานระบบวิเคราะห์</p>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown("<div style='padding:20px; border-right:1px solid rgba(181,148,115,0.2);'>", unsafe_allow_html=True)
        st.markdown("#### 🔵 สมาชิก Google")
        res = oauth2.authorize_button(
            name="Login with Google",
            icon="https://www.iconpacks.net/icons/2/free-google-icon-2039-thumb.png",
            redirect_uri="https://bhoonkharn-ai.streamlit.app", 
            scope="openid email profile", key="google_login"
        )
        if res:
            payload = json.loads(base64.urlsafe_b64decode(res["token"]["id_token"].split(".")[1] + "==").decode('utf-8'))
            st.session_state.user_info = {"name": payload.get("name"), "contact": payload.get("email"), "tier": "Premium"}
            sync_to_sheet(payload.get("name"), payload.get("email"), "Google Login")
            st.session_state.identified = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
        st.markdown("#### 📝 ลงทะเบียนทั่วไป")
        m_name = st.text_input("ชื่อ-นามสกุล")
        m_contact = st.text_input("อีเมล หรือ เบอร์โทรศัพท์")
        if st.button("เข้าสู่ระบบ", use_container_width=True):
            if m_name and m_contact:
                st.session_state.user_info = {"name": m_name, "contact": m_contact, "tier": "Standard"}
                sync_to_sheet(m_name, m_contact, "Manual Register")
                st.session_state.identified = True
                st.rerun()
            else: st.warning("กรุณากรอกข้อมูลให้ครบ")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. MAIN APP LOGIC (เมื่อระบุตัวตนแล้ว) ---
def get_engine():
    try:
        genai.configure(api_key=API_KEY)
        models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models.sort(reverse=True) # ค้นหารุ่นใหม่สุดก่อนเสมอ
        
        # เลือกโมเดลตาม Tier
        target_list = models if st.session_state.user_info.get("tier") == "Premium" else models[::-1]
        for m_name in target_list:
            try:
                m = genai.GenerativeModel(m_name)
                m.generate_content("test", generation_config={"max_output_tokens": 1})
                return m, "ONLINE"
            except: continue
        return None, "OFFLINE"
    except: return None, "OFFLINE"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = get_engine()

# --- HEADER NAV ---
st.markdown(f'<div class="top-nav"><div style="display:flex;align-items:center;"><div class="status-dot"></div><span class="status-text">{st.session_state.status}</span></div></div>', unsafe_allow_html=True)
nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang, key="lang_btn"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    with st.popover("👤"):
        st.markdown(f"**คุณ {st.session_state.user_info.get('name')}**")
        st.caption(f"Status: {st.session_state.user_info.get('tier')}")
        st.divider()
        st.caption("TOOLS") # กู้คืนแถวเครื่องมือตามข้อ 2
        st.button("ถอดแบบประเมินวัสดุ (Smart BOQ) [Soon]", use_container_width=True, disabled=True)
        st.button("เช็คราคาวัสดุ 5 ห้างหลัก [Soon]", use_container_width=True, disabled=True)
        st.button("แจ้งเตือนสภาพอากาศ [Soon]", use_container_width=True, disabled=True)
        st.divider()
        if st.button("ออกจากระบบ", type="primary", use_container_width=True):
            st.session_state.identified = False
            st.rerun()

# --- MAIN INTERFACE ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>Construction Inspection Intelligence</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📋 BLUEPRINT / แปลน</p>", unsafe_allow_html=True)
    bp = st.file_uploader("BP", type=['jpg','jpeg','png','pdf'], label_visibility="collapsed")
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📸 SITE PHOTO / หน้างาน</p>", unsafe_allow_html=True)
    site = st.file_uploader("SITE", type=['jpg','jpeg','png'], label_visibility="collapsed")
    if site: st.image(site)

if st.button("RUN ANALYSIS / เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site:
        with st.spinner("AI กำลังวิเคราะห์..."):
            try:
                # กำหนด Prompt ตามโครงสร้างที่ตกลงไว้ในข้อ 3
                prompt = """วิเคราะห์ภาพเทียบกันและตอบเป็น JSON ภาษาไทย: 
                {
                    "analysis":[], "risk":[], "checklist":[], "standard":[], 
                    "owner_guide":{"must_know":[], "self_check_manual":[], "special_advice":[]}, 
                    "current_task": ["ข้อย่อยที่ 1", "ข้อย่อยที่ 2", "ข้อย่อยที่ 3"], 
                    "next_task_from_this": ["ข้อย่อยถัดไป 1", "ข้อย่อยถัดไป 2", "ข้อย่อยถัดไป 3"],
                    "smart_materials":[{"name":"ชื่อวัสดุ", "unit_price":"฿..."}]
                } 
                ใน smart_materials ต้องมี 5-7 รายการ และงานต้องเป็นรายการย่อยเสมอ"""
                img_inp = Image.open(site) if site else Image.open(bp)
                res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
                st.session_state.json_data = json.loads(res.text)
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. RESULTS DISPLAY ---
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
    def render_sec(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            html = "<ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in d[key]]) + "</ul>"
            st.markdown(html, unsafe_allow_html=True)

    render_sec("🔍 วิเคราะห์หน้างาน", "analysis")
    render_sec("⚠️ จุดวิกฤตที่ต้องระวัง", "risk")
    
    if "current_task" in d:
        st.markdown("<div class='section-header'>🏗️ งานปัจจุบัน</div>", unsafe_allow_html=True)
        st.markdown("<ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in d["current_task"]]) + "</ul>", unsafe_allow_html=True)
    
    if "next_task_from_this" in d:
        st.markdown("<div class='section-header'>🏗️ งานถัดไปจากงานนี้</div>", unsafe_allow_html=True)
        st.markdown("<ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in d["next_task_from_this"]]) + "</ul>", unsafe_allow_html=True)

    if "smart_materials" in d:
        st.markdown("<div class='section-header'>🗓️ รายการวัสดุและประมาณการราคา</div>", unsafe_allow_html=True)
        for item in d["smart_materials"][:7]:
            st.markdown(f"<div class='mat-item'><a href='https://www.google.com/search?q={item['name']}+ราคา' target='_blank' class='mat-link'>{item['name']}</a><span class='mat-price'>{item.get('unit_price','')}</span></div>", unsafe_allow_html=True)

    # --- AI CHAT (สำหรับพรีเมียมเก็บประวัติ / สแตนดาร์ดเคลียร์ทิ้ง) ---
    st.divider()
    st.markdown("<div class='section-header'>💬 ปรึกษา AI เพิ่มเติม</div>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt_chat := st.chat_input("ถามคำถามของคุณ..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt_chat})
        with st.chat_message("user"): st.markdown(prompt_chat)
        with st.chat_message("assistant"):
            ctx = f"ข้อมูลวิเคราะห์: {json.dumps(st.session_state.json_data)} \n\nคำถาม: {prompt_chat}"
            response = st.session_state.engine.generate_content(ctx)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# --- FOOTER ---
st.markdown(f"""
<div class='footer-box'>
    <div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem;'>
        BHOON KHARN | 088-777-6566 | Line ID: bhoonkharn
    </div>
    <div style='font-size:0.7rem; color:#666; max-width:800px; margin:15px auto; line-height:1.5;'>
        <b>หมายเหตุ:</b> ระบบ AI ให้คำแนะนำเบื้องต้นเท่านั้น ไม่สามารถแทนที่การตรวจสอบโดยวิศวกรวิชาชีพได้ 
        กรุณาปรึกษาผู้เชี่ยวชาญก่อนดำเนินการใดๆ | Version final_1.4
    </div>
</div>
""", unsafe_allow_html=True)
