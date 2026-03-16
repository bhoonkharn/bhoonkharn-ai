import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import os
from datetime import datetime

# --- 1. CONFIG & STYLE (ปรับแต่งจากโค้ดเดิมของคุณ + SRS Phase 1) ---
st.set_page_config(
    page_title="BHOON KHARN AI", 
    page_icon="logo.png", # ไอคอนบน Tab Browser
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; }
    
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    
    /* ปิด Sidebar ตามสั่ง */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-bottom: 0px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; padding: 0 10%; }
    
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px; }
    
    .content-list { line-height: 2; color: #E0E0E0; margin-bottom: 20px; list-style-type: none; padding-left: 0; }
    .content-list li { margin-bottom: 10px; padding-left: 25px; position: relative; }
    .content-list li::before { content: "•"; color: var(--bk-gold); position: absolute; left: 0; font-weight: bold; }
    
    .next-task-box { background: rgba(181, 148, 115, 0.08); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 20px; margin: 15px 0; color: #E0E0E0; line-height: 1.8; }
    .owner-box { border-left: 5px solid var(--bk-gold); padding: 20px; background: rgba(181, 148, 115, 0.07); border-radius: 0 15px 15px 0; margin: 25px 0; }

    /* Top Nav Styling */
    .top-nav { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 15px; z-index: 10000; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; margin-right: 5px; }
    .status-text { font-size: 0.65rem; color: #B59473; font-weight: 700; letter-spacing: 1px; }
    .mat-link { color: var(--bk-gold); text-decoration: none; font-weight: 700; font-size: 1rem; }
    .mat-link:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบอัจฉริยะ: วนหา Model แบบไม่จำกัดรุ่น) ---
# ดึง API KEY จาก Secret เพื่อความปลอดภัย
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyC1SVrdU2iUOuvHCVnk0BfFE93vMlImEEc")

def init_ai_engine():
    try:
        genai.configure(api_key=API_KEY)
        # ดึงรายชื่อ Model ทั้งหมดที่รองรับ (No Hardcode)
        try:
            available_models = [m.name.replace("models/", "") for m in genai.list_models() 
                              if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()]
        except:
            available_models = ["gemini-1.5-flash", "gemini-1.5-pro"]

        # ฟังก์ชันจัดเรียง (ใหม่ไปเก่า)
        def sort_key(name):
            match = re.search(r'(\d+\.\d+)', name)
            version = float(match.group(1)) if match else 1.0
            cost_tier = 0 if 'flash' in name else (1 if 'pro' in name else 2)
            return (version, -cost_tier)

        available_models.sort(key=sort_key, reverse=True)

        # Privilege Logic (Admin vs User)
        # จำลองสถานะเบื้องต้น:Admin/ครั้งแรกใช้ตัวใหม่สุด, ครั้งถัดไปวนหาตัวประหยัด
        if st.session_state.get("is_admin", True) or st.session_state.get("usage_count", 0) == 0:
            target_list = available_models
        else:
            target_list = available_models[::-1]

        # Loop & Try: วนทดสอบทีละตัวจนกว่าจะเจอตัวที่ใช้งานได้จริง
        for model_name in target_list:
            try:
                model = genai.GenerativeModel(model_name)
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, f"ONLINE ({model_name})"
            except:
                continue
        return None, "OFFLINE"
    except Exception as e:
        return None, f"OFFLINE (Error: {e})"

# Session States
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}
if "is_admin" not in st.session_state: st.session_state.is_admin = True # ตั้งค่าทดสอบ Admin

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# --- 3. TOP NAVIGATION & 5. HEADER ---
st.markdown(f"""
<div class="top-nav">
    <div style="display:flex; align-items:center;">
        <div class="status-dot"></div>
        <span class="status-text">{st.session_state.status}</span>
    </div>
</div>
""", unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang):
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

# --- 4. MAIN UI ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์หน้างานก่อสร้างล่วงหน้าด้วย AI Vision อัจฉริยะ</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📋 BLUEPRINT / แปลน</p>", unsafe_allow_html=True)
    bp = st.file_uploader("BP", type=['jpg','jpeg','png','pdf'], label_visibility="collapsed")
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    st.markdown("<p style='text-align:center; color:var(--bk-gold); font-weight:700;'>📸 SITE PHOTO / หน้างาน</p>", unsafe_allow_html=True)
    site = st.file_uploader("SITE", type=['jpg','jpeg','png'], label_visibility="collapsed")
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine: 
        st.session_state.engine, st.session_state.status = init_ai_engine()
        if not st.session_state.engine:
            st.error("ระบบไม่พร้อมใช้งาน")
            return
            
    with st.spinner("AI กำลังวิเคราะห์..."):
        try:
            prompt = """วิเคราะห์ภาพและตอบเป็น JSON ภาษาไทยเท่านั้น:
            {
                "analysis": ["ข้อ 1", "ข้อ 2"],
                "risk": ["เสี่ยง 1", "เสี่ยง 2"],
                "checklist": ["ตรวจ 1", "ตรวจ 2"],
                "standard": ["มาตรฐาน 1", "มาตรฐาน 2"],
                "next_task": "งานถัดไป 1 ประโยค",
                "materials": ["วัสดุ 1", "วัสดุ 2", "วัสดุ 3", "วัสดุ 4", "วัสดุ 5"],
                "owner_note": ["แนะนำ 1", "แนะนำ 2"]
            }
            ห้ามระบุยี่ห้อ ห้ามใช้ข้อมูลสุ่ม"""
            
            img_inp = Image.open(site) if site else Image.open(bp)
            res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
            st.session_state.json_data = json.loads(res.text)
            st.session_state.usage_count += 1
        except Exception as e: st.error(f"Error: {e}")

if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. RESULTS & SEARCH LINKS (ปรับปรุงใหม่ตามสั่ง) ---
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
    
    def render_sec(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            items = d[key]
            if isinstance(items, list):
                list_html = "<ul class='content-list'>" + "".join([f"<li><b>{i}</b></li>" for i in items]) + "</ul>"
                st.markdown(list_html, unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='margin-bottom:20px;'><b>{items}</b></div>", unsafe_allow_html=True)

    render_sec("🔍 วิเคราะห์หน้างาน", "analysis")
    render_sec("⚠️ จุดวิกฤตที่ต้องระวัง", "risk")
    render_sec("📝 เทคนิคการตรวจงาน", "checklist")
    render_sec("🏗️ มาตรฐานวิศวกรรม", "standard")

    if "next_task" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไป</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='next-task-box'><b>{d['next_task']}</b></div>", unsafe_allow_html=True)

    # รายการวัสดุ 5-7 รายการ แบบ Text Link (ไม่มีรูปภาพ)
    if "materials" in d:
        st.markdown("<div class='section-header'>🗓️ รายการวัสดุที่ต้องเตรียม</div>", unsafe_allow_html=True)
        for item in d["materials"][:7]:
            search_url = f"https://www.google.com/search?q={item}"
            st.markdown(f"• <a href='{search_url}' target='_blank' class='mat-link'>{item}</a>", unsafe_allow_html=True)

    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 แนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        items = d["owner_note"]
        if isinstance(items, list):
            list_html = "<div class='owner-box'><ul class='content-list' style='margin-bottom:0;'>" + "".join([f"<li><b>{i}</b></li>" for i in items]) + "</ul></div>"
            st.markdown(list_html, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; margin-top:50px; color:#4A3F35; font-size:0.7rem;'>BHOON KHARN | PRIVATE SYSTEM</div>", unsafe_allow_html=True)
