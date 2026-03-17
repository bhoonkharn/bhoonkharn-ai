import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import base64
from streamlit_oauth import OAuth2Component

# --- 1. CONFIG & STYLE (ปรับตามข้อ 2 และ 3) ---
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
    /* ข้อ 3: ลบกล่องสี่เหลี่ยมใต้ชื่อออก ให้เหลือแค่ตัวหนังสือ */
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; letter-spacing: 2px; }
    
    /* ข้อ 3: กรอบอัปโหลดไฟล์ให้สมส่วน */
    .upload-frame { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(181, 148, 115, 0.2); border-radius: 12px; padding: 25px; margin-bottom: 20px; }
    
    .section-header { color: var(--bk-gold); font-size: 1.15rem; font-weight: 700; margin-top: 30px; margin-bottom: 15px; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 10px; }
    .content-list { line-height: 1.8; color: #E0E0E0; list-style-type: none; padding-left: 0; width: 100%; }
    .content-list li { margin-bottom: 12px; padding-left: 20px; border-left: 3px solid var(--bk-gold); display: block; }
    
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 15px; z-index: 10000; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #28a745; box-shadow: 0 0 8px #28a745; margin-right: 8px; }
    /* ข้อ 3: ตัดชื่อรุ่นออก เหลือแค่ ONLINE */
    .status-text { font-size: 0.75rem; color: #B59473; font-weight: 700; letter-spacing: 1.5px; }
    
    /* ข้อ 2: ปุ่มเปลี่ยนภาษาล็อคบรรทัดเดียว */
    div.stButton > button[key="lang_btn"] { min-width: 85px !important; width: 85px !important; padding: 0px !important; height: 35px !important; }

    button[kind="primary"] { 
        background-color: rgba(181, 148, 115, 0.1) !important; 
        color: var(--bk-gold) !important; 
        border: 1px solid var(--bk-gold) !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        width: 100% !important;
    }
    button[kind="primary"]:hover { background-color: var(--bk-gold) !important; color: var(--bk-dark) !important; }

    .mat-item { margin-bottom: 15px; padding: 10px 0; border-bottom: 1px solid rgba(181, 148, 115, 0.1); }
    .mat-link { color: var(--bk-gold); text-decoration: none; font-weight: 700; font-size: 1.1rem; }
    .mat-price { color: #28a745; font-size: 0.95rem; font-weight: 700; margin-left: 12px; }
    
    .owner-box { border-left: 4px solid var(--bk-gold); padding: 5px 20px; background: rgba(181, 148, 115, 0.05); margin: 20px 0; border-radius: 0 10px 10px 0; width: 100%; }
    .footer-box { text-align: center; margin-top: 40px; padding: 30px 0; border-top: 1px solid rgba(181, 148, 115, 0.1); }
</style>
""", unsafe_allow_html=True)

# --- Initial State ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}

# --- 2. ENGINE & LOGIN LOGIC (ข้อ 1) ---
CLIENT_ID = "358673361686-q6nuqn6tqefffcrm9krtcv1u11rmvt8j.apps.googleusercontent.com"
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
ADMIN_EMAIL = "bhoonkharn@gmail.com"
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/v2/auth", "https://oauth2.googleapis.com/token", "https://oauth2.googleapis.com/token")

def trigger_login():
    st.markdown("<div style='text-align:center; padding:20px; border:1px solid var(--bk-gold); border-radius:10px; background:rgba(181,148,115,0.05);'>", unsafe_allow_html=True)
    st.markdown("### 🔒 สิทธิ์ใช้งานฟรีหมดแล้ว")
    st.write("กรุณาเข้าสู่ระบบเพื่อใช้งานต่อและบันทึกประวัติการวิเคราะห์")
    res = oauth2.authorize_button(
        name="Sign in with Google",
        icon="https://www.iconpacks.net/icons/2/free-google-icon-2039-thumb.png",
        redirect_uri="https://bhoonkharn-ai.streamlit.app", 
        scope="openid email profile",
        key="google_login",
        extras_params={"prompt": "select_account"}
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if res:
        st.session_state["auth"] = res["token"]
        st.rerun()

if "auth" in st.session_state and "user_info" not in st.session_state:
    try:
        payload = st.session_state["auth"]["id_token"].split(".")[1]
        payload += "=" * ((4 - len(payload) % 4) % 4)
        st.session_state["user_info"] = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))
    except: st.session_state["user_info"] = {"email": "guest", "name": "User"}

# ข้อ 1: Model Hunter (ค้นหารุ่นใหม่ก่อนเสมอ)
def get_engine():
    try:
        genai.configure(api_key=API_KEY)
        models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        def model_rank(name):
            v_match = re.search(r'(\d+\.\d+)', name)
            v = float(v_match.group(1)) if v_match else 1.0
            tier = 0 if 'flash' in name else (1 if 'pro' in name else 2)
            return (v, -tier)
        
        models.sort(key=model_rank, reverse=True) # ใหม่สุดอยู่บน

        is_logged = "auth" in st.session_state
        is_admin = st.session_state.get("user_info", {}).get("email") == ADMIN_EMAIL
        
        # กฎการเลือกโมเดล ( Tiering )
        if is_admin or is_logged or st.session_state.usage_count == 0:
            target_list = models # เริ่มค้นหาจากตัวใหม่ที่สุด
        else:
            target_list = models[::-1] # เริ่มค้นหาจากตัวเก่าที่สุด

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

# --- 3. HEADER & NAV ---
st.markdown(f'<div class="top-nav"><div style="display:flex;align-items:center;"><div class="status-dot"></div><span class="status-text">{st.session_state.status}</span></div></div>', unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang, key="lang_btn"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    with st.popover("👤"):
        if "auth" in st.session_state:
            st.markdown(f"**คุณ {st.session_state['user_info'].get('name')}**")
            if st.button("ออกจากระบบ", type="primary", use_container_width=True):
                del st.session_state["auth"]
                st.session_state.chat_history = []
                st.rerun()
        else:
            st.markdown("**GUEST**")
            if st.button("เข้าสู่ระบบ", use_container_width=True): trigger_login()

# --- 4. MAIN INTERFACE ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>Construction Inspection Intelligence</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="upload-frame">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📋 BLUEPRINT / แปลน</p>", unsafe_allow_html=True)
    bp = st.file_uploader("BP", type=['jpg','jpeg','png','pdf'], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    st.markdown('<div class="upload-frame">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📸 SITE PHOTO / หน้างาน</p>", unsafe_allow_html=True)
    site = st.file_uploader("SITE", type=['jpg','jpeg','png'], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if site: st.image(site)

if st.button("RUN ANALYSIS / เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if st.session_state.usage_count >= 1 and "auth" not in st.session_state:
        trigger_login()
    elif bp or site:
        with st.spinner("AI กำลังวิเคราะห์..."):
            try:
                # ข้อ 2, 3: วิเคราะห์งานถัดไป 3 ข้อ + วัสดุ 5-7 รายการ
                prompt = 'วิเคราะห์ภาพเทียบกันและตอบเป็น JSON ภาษาไทย: {"analysis":[], "risk":[], "checklist":[], "standard":[], "owner_guide":{"must_know":[], "self_check_manual":[], "special_advice":[]}, "next_3_tasks":["1","2","3"], "smart_materials":[{"name":"ชื่อวัสดุ", "unit_price":"฿..."}]}'
                img_inp = Image.open(site) if site else Image.open(bp)
                res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
                st.session_state.json_data = json.loads(res.text)
                st.session_state.usage_count += 1
                st.rerun()
            except Exception as e: st.error(f"Analysis Error: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. RESULTS DISPLAY ---
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
    
    # ข้อ 6: รวมหมวดเจ้าของบ้าน
    if "owner_guide" in d:
        st.markdown("<div class='section-header'>🏠 สิ่งที่เจ้าของบ้านควรรู้และคู่มือตรวจสอบ</div>", unsafe_allow_html=True)
        g = d["owner_guide"]
        if g.get("must_know"):
            st.markdown("**📌 ข้อมูลสำคัญที่ควรรู้:**")
            st.markdown("<div class='owner-box'><ul class='content-list'>" + "".join([f"<li>{i}</li>" for i in g["must_know"]]) + "</ul></div>", unsafe_allow_html=True)
        if g.get("self_check_manual"):
            st.markdown("**✅ คู่มือตรวจสอบเบื้องต้น:**")
            st.markdown("<ul class='content-list'>" + "".join([f"<li>{i}</li>" for i in g["self_check_manual"]]) + "</ul>", unsafe_allow_html=True)
        if g.get("special_advice"):
            st.markdown("**💡 คำแนะนำเพิ่มเติม:**")
            st.info("\n".join(g["special_advice"]))

    # ข้อ 3: งานลำดับถัดไป 3 ขั้นตอน
    if "next_3_tasks" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไป (เตรียมตัว 3 ขั้นตอน)</div>", unsafe_allow_html=True)
        for i, t in enumerate(d["next_3_tasks"], 1):
            st.markdown(f"<div class='owner-box'><b>{i}. {t}</b></div>", unsafe_allow_html=True)

    # ข้อ 2, 4: วัสดุ 5-7 รายการพร้อมราคา
    if "smart_materials" in d:
        st.markdown("<div class='section-header'>🗓️ รายการวัสดุและประมาณการราคา</div>", unsafe_allow_html=True)
        for item in d["smart_materials"][:7]:
            url = f"https://www.google.com/search?q={item['name']}+ราคา"
            st.markdown(f"<div class='mat-item'><a href='{url}' target='_blank' class='mat-link'>{item['name']}</a> <span class='mat-price'>{item.get('unit_price','')}</span></div>", unsafe_allow_html=True)

    # --- 6. AI CHAT (ข้อ 3: วางเหนือ Footer) ---
    st.divider()
    st.markdown("<div class='section-header'>💬 ปรึกษา AI เพิ่มเติม</div>", unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt_chat := st.chat_input("พิมพ์คำถามของคุณ..."):
        if "auth" not in st.session_state:
            trigger_login()
        else:
            st.session_state.chat_history.append({"role": "user", "content": prompt_chat})
            with st.chat_message("user"): st.markdown(prompt_chat)
            with st.chat_message("assistant"):
                chat_engine, _ = get_engine()
                full_ctx = f"จากผลวิเคราะห์: {json.dumps(st.session_state.json_data)} \n\nคำถาม: {prompt_chat}"
                response = chat_engine.generate_content(full_ctx)
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# --- 7. FOOTER (ข้อ 4 & 5) ---
st.markdown(f"""
<div class='footer-box'>
    <div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem;'>
        BHOON KHARN | 088-777-6566 | Line ID: bhoonkharn
    </div>
    <div style='font-size:0.7rem; color:#666; max-width:800px; margin:15px auto; line-height:1.5;'>
        <b>หมายเหตุ:</b> ระบบ AI ให้คำแนะนำเบื้องต้นเท่านั้น ไม่สามารถแทนที่การตรวจสอบโดยวิศวกรวิชาชีพได้ 
        กรุณาปรึกษาผู้เชี่ยวชาญก่อนดำเนินการใดๆ | Version 2.1 Final 1.1
    </div>
</div>
""", unsafe_allow_html=True)
