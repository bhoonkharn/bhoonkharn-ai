import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import base64
from streamlit_oauth import OAuth2Component

# --- 1. CONFIG & STYLE (ปรับปรุง CSS ตามข้อ 2 และ 6) ---
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
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; letter-spacing: 2px; }
    
    .section-header { color: var(--bk-gold); font-size: 1.15rem; font-weight: 700; margin-top: 30px; margin-bottom: 15px; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 10px; }
    .upload-box { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(181, 148, 115, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 20px; }

    .content-list { line-height: 1.8; color: #E0E0E0; list-style-type: none; padding-left: 0; margin-bottom: 25px; display: block; width: 100%; }
    .content-list li { margin-bottom: 12px; padding-left: 20px; border-left: 3px solid var(--bk-gold); display: block; white-space: normal; }
    
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 15px; z-index: 10000; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #28a745; box-shadow: 0 0 8px #28a745; margin-right: 8px; }
    .status-text { font-size: 0.75rem; color: #B59473; font-weight: 700; letter-spacing: 1.5px; }
    
    /* ข้อ 2: แก้ปุ่มเปลี่ยนภาษาให้เป็นบรรทัดเดียว */
    div.stButton > button[key="lang_btn"] { min-width: 65px !important; width: 65px !important; padding: 0px !important; }

    button[kind="primary"] { 
        background-color: rgba(181, 148, 115, 0.1) !important; 
        color: var(--bk-gold) !important; 
        border: 1px solid var(--bk-gold) !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
    }
    button[kind="primary"]:hover { background-color: var(--bk-gold) !important; color: var(--bk-dark) !important; }

    .mat-item { margin-bottom: 20px; }
    .mat-link { color: var(--bk-gold); text-decoration: none; font-weight: 700; font-size: 1.1rem; }
    .mat-price { color: #28a745; font-size: 0.9rem; font-weight: 700; margin-left: 10px; }
    .mat-preview { color: #A09080; font-size: 0.85rem; margin-top: 5px; font-style: italic; line-height: 1.4; }
    
    .owner-box { border-left: 4px solid var(--bk-gold); padding: 5px 20px; background: rgba(181, 148, 115, 0.05); margin: 20px 0; border-radius: 0 10px 10px 0; width: 100%; }
    
    /* Footer & Disclaimer (ข้อ 4, 5) */
    .footer-box { text-align: center; margin-top: 60px; padding: 40px 0; border-top: 1px solid rgba(181, 148, 115, 0.1); }
    .disclaimer { font-size: 0.7rem; color: #666; max-width: 700px; margin: 15px auto; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# --- Initial Session States ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}

# --- 2. ระบบ LOGIN GOOGLE (ข้อ 1: Freemium Logic) ---
CLIENT_ID = "358673361686-q6nuqn6tqefffcrm9krtcv1u11rmvt8j.apps.googleusercontent.com"
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
ADMIN_EMAIL = "bhoonkharn@gmail.com"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/v2/auth", "https://oauth2.googleapis.com/token", "https://oauth2.googleapis.com/token")

# ฟังก์ชันแสดงหน้า Login
def show_login_page():
    st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#A09080; letter-spacing:3px;'>กรุณาเข้าสู่ระบบเพื่อใช้งานต่อ</p>", unsafe_allow_html=True)
    l_c1, l_c2, l_c3 = st.columns([1.2, 1, 1.2])
    with l_c2:
        res = oauth2.authorize_button(
            name="Sign in with Google",
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

# เงื่อนไข Freemium: ถ้าใช้ไปแล้ว 1 ครั้ง และยังไม่ล็อกอิน ให้แสดงหน้าล็อกอิน
if st.session_state.usage_count >= 1 and "auth" not in st.session_state:
    show_login_page()

# ถอดรหัส User Info
if "auth" in st.session_state and "user_info" not in st.session_state:
    try:
        payload = st.session_state["auth"]["id_token"].split(".")[1]
        payload += "=" * ((4 - len(payload) % 4) % 4)
        st.session_state["user_info"] = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))
    except:
        st.session_state["user_info"] = {"email": "guest", "name": "Guest User"}

# --- 3. ENGINE (Dynamic Model Hunter - Privilege & Token Control) ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

def init_ai_engine(is_chat=False):
    try:
        genai.configure(api_key=API_KEY)
        is_logged_in = "auth" in st.session_state
        
        # สายฟรี (ยังไม่ Login) -> ใช้ Flash เสมอเพื่อประหยัด Token
        if not is_logged_in:
            return genai.GenerativeModel("gemini-1.5-flash"), "ONLINE (GUEST)"

        # สายสมาชิก/Admin -> ค้นหาโมเดลที่ดีที่สุด
        raw_models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()]
        raw_models.sort(reverse=True) # เอาตัวใหม่ขึ้นก่อน
        
        for m_name in raw_models:
            try:
                m = genai.GenerativeModel(m_name)
                m.generate_content("test", generation_config={"max_output_tokens": 1})
                return m, "ONLINE"
            except: continue
        return genai.GenerativeModel("gemini-1.5-flash"), "ONLINE (STABLE)"
    except: return None, "OFFLINE"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# --- HEADER (Top Nav) ---
st.markdown(f'<div class="top-nav"><div style="display:flex;align-items:center;"><div class="status-dot"></div><span class="status-text">{st.session_state.status}</span></div></div>', unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang, key="lang_btn"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    with st.popover("👤"):
        if "auth" in st.session_state:
            u_email = st.session_state["user_info"].get("email", "")
            st.markdown(f"**คุณ {st.session_state['user_info'].get('name', 'USER')}**")
            st.caption(f"{'ADMIN STATUS' if u_email == ADMIN_EMAIL else 'MEMBER ACCESS'}")
            st.divider()
            if st.button("SIGN OUT", type="primary", use_container_width=True):
                del st.session_state["auth"]
                st.session_state.chat_history = [] # เคลียร์แชทเมื่อออก
                st.rerun()
        else:
            st.markdown("**GUEST ACCESS**")
            st.caption("ใช้งานได้จำกัด 1 ครั้งฟรี")
            if st.button("LOGIN TO SAVE DATA", use_container_width=True):
                show_login_page()

# --- MAIN UI ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>Construction Inspection Intelligence</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📋 BLUEPRINT / แปลน</p>", unsafe_allow_html=True)
    bp = st.file_uploader("BP", type=['jpg','jpeg','png','pdf'], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📸 SITE PHOTO / หน้างาน</p>", unsafe_allow_html=True)
    site = st.file_uploader("SITE", type=['jpg','jpeg','png'], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if site: st.image(site)

if st.button("RUN ANALYSIS / เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site:
        with st.spinner("AI กำลังวิเคราะห์..."):
            try:
                prompt = """วิเคราะห์ภาพเปรียบเทียบและตอบเป็น JSON ภาษาไทย: 
                {
                    "analysis":[], "risk":[], "checklist":[], "standard":[], 
                    "owner_guide":{ "must_know": [], "self_check_manual": [], "special_advice": [] }, 
                    "next_3_tasks": ["งาน 1", "งาน 2", "งาน 3"], 
                    "smart_materials": [{"name": "ชื่อวัสดุ", "unit_price": "฿...", "preview": "สรุปสเปกสั้นๆ"}]
                }"""
                img_inp = Image.open(site) if site else Image.open(bp)
                res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
                st.session_state.json_data = json.loads(res.text)
                st.session_state.usage_count += 1
                st.rerun() # Refresh เพื่ออัปเดตสถานะ Login หากจำเป็น
            except Exception as e: st.error(f"Analysis Error: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- RESULTS DISPLAY ---
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
    
    def render_sec(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            items = d[key]
            if isinstance(items, list) and items:
                html = "<ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in items]) + "</ul>"
                st.markdown(html, unsafe_allow_html=True)

    render_sec("🔍 วิเคราะห์หน้างาน", "analysis")
    render_sec("⚠️ จุดวิกฤตที่ต้องระวัง", "risk")
    render_sec("📝 เทคนิคการตรวจงาน", "checklist")
    render_sec("🏗️ มาตรฐานวิศวกรรม", "standard")
    
    # ข้อ 6: สิ่งที่เจ้าของบ้านควรรู้ (รวมหมวด)
    if "owner_guide" in d:
        st.markdown("<div class='section-header'>🏠 สิ่งที่เจ้าของบ้านควรรู้และคู่มือตรวจสอบ</div>", unsafe_allow_html=True)
        g = d["owner_guide"]
        if "must_know" in g:
            st.markdown("**📌 ความรู้พื้นฐานสำหรับหน้างานนี้:**")
            st.markdown("<div class='owner-box'><ul class='content-list'>" + "".join([f"<li>{i}</li>" for i in g["must_know"]]) + "</ul></div>", unsafe_allow_html=True)
        if "self_check_manual" in g:
            st.markdown("**✅ คู่มือการตรวจสอบด้วยตัวเอง:**")
            st.markdown("<ul class='content-list'>" + "".join([f"<li>{i}</li>" for i in g["self_check_manual"]]) + "</ul>", unsafe_allow_html=True)
        if "special_advice" in g:
            st.markdown("**💡 คำแนะนำเพิ่มเติม:**")
            st.info("\n".join(g["special_advice"]))

    # ข้อ 3: งานถัดไป (3 ขั้นตอน)
    if "next_3_tasks" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไป (3 ขั้นตอนถัดไป)</div>", unsafe_allow_html=True)
        for i, task in enumerate(d["next_3_tasks"], 1):
            st.markdown(f"<div class='owner-box'><b>{i}. {task}</b></div>", unsafe_allow_html=True)

    # ข้อ 4: รายการวัสดุอัจฉริยะ (ราคา + พรีวิว)
    if "smart_materials" in d:
        st.markdown("<div class='section-header'>🗓️ รายการวัสดุและประมาณการราคา (เช็คราคา)</div>", unsafe_allow_html=True)
        for item in d["smart_materials"][:7]:
            url = f"https://www.google.com/search?q={item['name']}+ราคา"
            st.markdown(f"""
            <div class='mat-item'>
                <a href='{url}' target='_blank' class='mat-link'>{item['name']}</a>
                <span class='mat-price'>{item.get('unit_price', 'เช็คราคา')}</span>
                <div class='mat-preview'>💡 AI Preview: {item.get('preview', '')}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- ข้อ 3: ระบบแชท AI (AI Chat) ---
    st.divider()
    st.markdown("<div class='section-header'>💬 สอบถาม AI เพิ่มเติมเกี่ยวกับผลวิเคราะห์นี้</div>", unsafe_allow_html=True)
    
    # แสดงประวัติแชท
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt_chat := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
        # เช็คสิทธิ์ก่อนแชทครั้งที่ 2 (ตามกฎ Login)
        if st.session_state.usage_count >= 1 and "auth" not in st.session_state:
            show_login_page()
            
        st.session_state.chat_history.append({"role": "user", "content": prompt_chat})
        with st.chat_message("user"):
            st.markdown(prompt_chat)

        with st.chat_message("assistant"):
            chat_engine, _ = init_ai_engine(is_chat=True)
            full_context = f"จากผลการวิเคราะห์งานก่อสร้าง: {json.dumps(st.session_state.json_data)} \n\nคำถามผู้ใช้: {prompt_chat}"
            response = chat_engine.generate_content(full_context)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# --- 4, 5. FOOTER (เพิ่ม LINE ID & Disclaimer) ---
st.markdown(f"""
<div class='footer-box'>
    <div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem;'>
        BHOON KHARN | 088-777-6566 | Line ID: bhoonkharn
    </div>
    <div class='disclaimer'>
        <b>หมายเหตุข้อจำกัดของ AI:</b> ระบบ BHOON KHARN AI ให้คำแนะนำเบื้องต้นจากข้อมูลภาพถ่ายเท่านั้น 
        ผลลัพธ์อาจมีความคลาดเคลื่อนตามคุณภาพรูปภาพ <u>ไม่สามารถแทนที่การตรวจสอบโดยวิศวกรวิชาชีพได้</u> 
        กรุณาปรึกษาวิศวกรหรือผู้ควบคุมงานก่อนดำเนินการใดๆ
    </div>
</div>
""", unsafe_allow_html=True)
