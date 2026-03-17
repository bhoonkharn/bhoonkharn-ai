import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# --- 1. CONFIG & STYLE (ปรับปรุงตามข้อ 2, 3, 6) ---
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
    
    .section-header { color: var(--bk-gold); font-size: 1.1rem; font-weight: 700; margin-top: 25px; margin-bottom: 12px; border-bottom: 1px solid rgba(181, 148, 115, 0.2); padding-bottom: 8px; }
    
    /* แก้ไขปัญหาตัวหนังสือแนวตั้ง (ข้อ 6) */
    .content-list { line-height: 1.8; color: #E0E0E0; list-style-type: none; padding-left: 0; margin-bottom: 20px; width: 100%; }
    .content-list li { margin-bottom: 12px; padding-left: 20px; border-left: 2px solid var(--bk-gold); white-space: normal; word-wrap: break-word; }
    
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 15px; z-index: 10000; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #28a745; box-shadow: 0 0 8px #28a745; margin-right: 8px; }
    .status-text { font-size: 0.7rem; color: #B59473; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }
    
    /* ปุ่มเปลี่ยนภาษา (ข้อ 2) */
    div.stButton > button[key="lang_btn"] { width: 50px !important; min-width: 50px !important; padding: 0px !important; }

    /* ปุ่มวิเคราะห์สีทองพรีเมียม (ข้อ 3) */
    div.stButton > button[type="primary"] { 
        background-color: transparent !important; 
        color: var(--bk-gold) !important; 
        border: 1px solid var(--bk-gold) !important;
        border-radius: 5px !important;
        transition: 0.3s !important;
        font-weight: 700 !important;
    }
    div.stButton > button[type="primary"]:hover { 
        background-color: var(--bk-gold) !important; 
        color: var(--bk-dark) !important; 
    }

    .mat-link { color: var(--bk-gold); text-decoration: none; font-weight: 700; font-size: 1rem; transition: 0.2s; }
    .mat-link:hover { color: #F5F5F5; text-decoration: underline; }
    .owner-box { border-left: 4px solid var(--bk-gold); padding: 5px 20px; background: rgba(181, 148, 115, 0.05); margin: 20px 0; border-radius: 0 8px 8px 0; }
</style>
""", unsafe_allow_html=True)

# Initial State
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}
if "is_admin" not in st.session_state: st.session_state.is_admin = True

# --- ENGINE (Dynamic Model Hunter) ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

def init_ai_engine():
    try:
        genai.configure(api_key=API_KEY)
        try:
            raw_models = [m.name.replace("models/", "") for m in genai.list_models() 
                         if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()]
        except:
            raw_models = ["gemini-3-flash-preview", "gemini-1.5-flash", "gemini-1.5-pro"]
        
        def sort_logic(name):
            v_match = re.search(r'(\d+\.\d+)', name)
            v = float(v_match.group(1)) if v_match else (3.0 if 'gemini-3' in name else 1.0)
            tier = 0 if 'flash' in name else (1 if 'pro' in name else 2)
            return (v, -tier)
        
        raw_models.sort(key=sort_logic, reverse=True)
        target_list = raw_models if (st.session_state.is_admin or st.session_state.usage_count == 0) else raw_models[::-1]

        for m_name in target_list:
            try:
                m = genai.GenerativeModel(m_name)
                m.generate_content("test", generation_config={"max_output_tokens": 1})
                return m, "ONLINE" # ตัดชื่อรุ่นออกตามข้อ 1
            except: continue
        return None, "OFFLINE"
    except: return None, "OFFLINE"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# --- TOP NAVIGATION ---
st.markdown(f'<div class="top-nav"><div style="display:flex;align-items:center;"><div class="status-dot"></div><span class="status-text">{st.session_state.status}</span></div></div>', unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang, key="lang_btn"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    with st.popover("👤"):
        st.markdown(f"**STATUS: {'ADMIN' if st.session_state.is_admin else 'USER'}**")
        st.divider()
        st.caption("TOOLS")
        st.button("ถอดแบบประเมินวัสดุ (Smart BOQ) [Coming Soon]", use_container_width=True, disabled=True)
        st.button("เช็คราคาวัสดุ 5 ห้างหลัก [Coming Soon]", use_container_width=True, disabled=True)
        st.button("แจ้งเตือนสภาพอากาศคิวเทปูน [Coming Soon]", use_container_width=True, disabled=True)
        st.divider()
        st.button("สร้างรายงาน PDF (TH/EN) [Upgrade to Pro]", use_container_width=True)
        st.button("Sign Out / ออกจากระบบ", type="primary", use_container_width=True)

# --- MAIN UI ---
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

# ปุ่มสีทองพรีเมียม (ข้อ 3)
if st.button("RUN ANALYSIS / เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site:
        with st.spinner("ANALYZING..."):
            try:
                # Prompt ปรับตามข้อ 4, 5, 7
                prompt = """วิเคราะห์ภาพเทียบกันและตอบเป็น JSON ภาษาไทย: 
                {
                    "analysis":[], "risk":[], "checklist":[], "standard":[], 
                    "owner_guide":[], "next_task":"", "next_materials":[], "owner_note":[]
                }
                ใน next_materials ให้ใส่มา 5-7 รายการพร้อมระบุว่าเป็นวัสดุสำหรับงานปัจจุบันหรือถัดไป"""
                img_inp = Image.open(site) if site else Image.open(bp)
                res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
                st.session_state.json_data = json.loads(res.text)
                st.session_state.usage_count += 1
            except Exception as e: st.error(f"Analysis Error: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- RESULTS DISPLAY (ข้อ 4, 5, 6, 7) ---
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
            elif items:
                st.markdown(f"<div style='margin-bottom:20px; padding-left:20px; border-left:2px solid var(--bk-gold);'><b>{items}</b></div>", unsafe_allow_html=True)

    render_sec("🔍 วิเคราะห์หน้างาน", "analysis")
    render_sec("⚠️ จุดวิกฤตที่ต้องระวัง", "risk")
    render_sec("📝 เทคนิคการตรวจงาน", "checklist")
    render_sec("🏗️ มาตรฐานวิศวกรรม", "standard")
    
    # ข้อ 4: สิ่งที่เจ้าของบ้านควรรู้และคู่มือการตรวจสอบด้วยตัวเอง
    render_sec("🏠 สิ่งที่เจ้าของบ้านควรรู้และคู่มือการตรวจสอบด้วยตัวเอง", "owner_guide")
    
    if "next_task" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไป</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom:20px; padding:15px; background:rgba(181,148,115,0.05); border-radius:8px;'><b>{d['next_task']}</b></div>", unsafe_allow_html=True)

    # ข้อ 5 & 7: วัสดุของงานปัจจุบันและงานถัดไป (5-7 รายการ + ลิงก์เช็คราคา)
    if "next_materials" in d:
        st.markdown("<div class='section-header'>🗓️ รายการวัสดุสำหรับงานนี้และงานถัดไป (เช็คราคา)</div>", unsafe_allow_html=True)
        for item in d["next_materials"][:7]:
            url = f"https://www.google.com/search?q={item}+ราคา"
            st.markdown(f"• <a href='{url}' target='_blank' class='mat-link'>{item}</a>", unsafe_allow_html=True)

    # ข้อ 6: แก้ไข Bug ตัวหนังสือแนวตั้ง (ใช้ Owner-box ที่กว้างขึ้น)
    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 คำแนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        html = "<div class='owner-box'><ul class='content-list' style='margin-bottom:0;'>" + "".join([f"<li><b>{i}</b></li>" for i in d["owner_note"]]) + "</ul></div>"
        st.markdown(html, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; margin-top:50px; color:#4A3F35; font-size:0.7rem;'>BHOON KHARN | PRIVATE SYSTEM</div>", unsafe_allow_html=True)
