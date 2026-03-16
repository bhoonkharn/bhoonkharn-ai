import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import os
import base64
from datetime import datetime
from streamlit_oauth import OAuth2Component

# --- 1. CONFIG & BRANDING (SRS Phase 1) ---
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
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; }
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px; }
    .content-list { line-height: 2; color: #E0E0E0; margin-bottom: 20px; list-style-type: none; padding-left: 0; }
    .content-list li { margin-bottom: 10px; padding-left: 25px; position: relative; }
    .content-list li::before { content: "•"; color: var(--bk-gold); position: absolute; left: 0; font-weight: bold; }
    .next-task-box { background: rgba(181, 148, 115, 0.08); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 20px; color: #E0E0E0; }
    .mat-table-header { background: var(--bk-brown); color: var(--bk-gold); font-weight: 700; padding: 15px; border-radius: 10px 10px 0 0; display: flex; align-items: center; }
    .mat-thumb-xl { width: 150px; height: 150px; border-radius: 12px; object-fit: cover; border: 2px solid rgba(181, 148, 115, 0.4); background: #2A2420; }
    .btn-search { color: var(--bk-gold) !important; text-decoration: none; border: 1px solid var(--bk-gold); padding: 8px 18px; border-radius: 8px; font-weight: bold; }

    /* Navigation SRS */
    .top-nav-container { position: fixed; top: 15px; right: 25px; display: flex; align-items: center; gap: 15px; z-index: 10000; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #28a745; box-shadow: 0 0 5px #28a745; margin-right: 5px; }
    .online-text { font-size: 0.6rem; color: #B59473; font-weight: 700; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE (ระบบจัดการลำดับการใช้) ---
if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "is_member" not in st.session_state: st.session_state.is_member = False
if "phone_number" not in st.session_state: st.session_state.phone_number = None
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "json_data" not in st.session_state: st.session_state.json_data = {}

# --- 3. AUTHENTICATION & DATA COLLECTION ---
CLIENT_ID = "358673361686-q6nuqn6tqefffcrm9krtcv1u11rmvt8j.apps.googleusercontent.com"
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/v2/auth", "https://oauth2.googleapis.com/token", "https://oauth2.googleapis.com/token", "https://oauth2.googleapis.com/revoke")

# บังคับล็อกอินถ้าใช้ครบ 1 ครั้ง (Guest Limit)
if st.session_state.usage_count >= 1 and "auth" not in st.session_state:
    st.markdown("<br><br><br><div style='text-align:center;'>", unsafe_allow_html=True)
    st.image("logo.png", width=120)
    st.markdown("<h2 style='color:var(--bk-gold);'>เข้าสู่ระบบเพื่อใช้งานต่อ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A09080;'>คุณใช้โควต้าทดลองใช้ฟรีครบแล้ว กรุณาลงชื่อเข้าใช้เพื่อรับสิทธิ์วิเคราะห์เพิ่มอีก 2 ครั้ง</p>", unsafe_allow_html=True)
    result = oauth2.authorize_button("Sign in with Google", "https://bhoonkharn-ai.streamlit.app", "openid email profile", icon="https://www.iconpacks.net/icons/2/free-google-icon-2039-thumb.png", key="google_login")
    if result:
        st.session_state["auth"] = result["token"]
        st.rerun()
    st.stop()

# เก็บเบอร์โทรสำหรับผู้ใช้ใหม่ที่เพิ่งล็อกอิน
if "auth" in st.session_state and st.session_state.phone_number is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<h3 style='text-align:center; color:var(--bk-gold);'>ยืนยันข้อมูลสมาชิก</h3>", unsafe_allow_html=True)
        phone = st.text_input("กรุณาระบุเบอร์โทรศัพท์เพื่อรับสิทธิ์สมาชิก", placeholder="08x-xxx-xxxx")
        if st.button("ยืนยันข้อมูล", use_container_width=True):
            if len(phone) >= 9:
                st.session_state.phone_number = phone
                st.success("ลงทะเบียนสำเร็จ!")
                st.rerun()
            else: st.error("กรุณาระบุเบอร์โทรศัพท์ที่ถูกต้อง")
    st.stop()

# --- 4. SMART ENGINE (ระบบสลับ Model ตามสถานะ) ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyC1SVrdU2iUOuvHCVnk0BfFE93vMlImEEc")

def init_ai_engine():
    try:
        genai.configure(api_key=API_KEY)
        # ดึง Model ทั้งหมด
        models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()]
        
        # ฟังก์ชันจัดเรียง (Newest First)
        def sort_key(name):
            v = float(re.search(r'(\d+\.\d+)', name).group(1)) if re.search(r'(\d+\.\d+)', name) else 0.0
            tier = 0 if 'flash' in name else (1 if 'pro' in name else 2)
            return (v, -tier)

        models.sort(key=sort_key, reverse=True) # ใหม่สุดอยู่บน

        # เลือก Model ตามเงื่อนไข
        target_model = None
        if st.session_state.is_member:
            target_model = models[0] # สมาชิกใช้ใหม่สุด
        elif st.session_state.usage_count == 0:
            target_model = models[0] # ครั้งแรก (Guest) ใช้ใหม่สุดเพื่อความประทับใจ
        else:
            target_model = models[-1] # ผู้ใช้ฟรี (หลังล็อกอิน) ใช้รุ่นเก่าสุดเพื่อประหยัด

        model = genai.GenerativeModel(target_model)
        # ทดสอบ Engine
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        return model, f"ONLINE ({target_model})"
    except Exception as e:
        return None, f"OFFLINE ({str(e)[:50]})"

st.session_state.engine, st.session_state.status = init_ai_engine()

# --- 5. TOP NAV & PROFILE ---
st.markdown(f'<div class="top-nav-container"><div class="status-dot"></div><span class="online-text">{st.session_state.status}</span></div>', unsafe_allow_html=True)

nav_c1, nav_c2, nav_c3 = st.columns([9.2, 0.4, 0.4])
with nav_c2:
    if st.button(st.session_state.lang):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
with nav_c3:
    if "auth" in st.session_state:
        with st.popover("👤"):
            st.markdown(f"**Member: {st.session_state.phone_number}**")
            st.button("SMART BOQ [Coming Soon]", use_container_width=True, disabled=True)
            if st.button("SIGN OUT", type="primary", use_container_width=True):
                del st.session_state["auth"]
                st.session_state.usage_count = 0 # รีเซ็ตการใช้เมื่อออก
                st.rerun()
    else: st.markdown("🌐")

# --- 6. MAIN CONTENT & ANALYSIS ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์หน้างานก่อสร้างล่วงหน้าด้วย AI Vision อัจฉริยะ</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน", type=['jpg','jpeg','png','pdf'], label_visibility="collapsed")
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'], label_visibility="collapsed")
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine:
        st.error("ขออภัย ระบบ AI ขัดข้องชั่วคราว")
        return
    
    # เช็คลิมิตผู้ใช้ฟรี (ล็อกอินแล้วได้อีก 2 ครั้ง รวมเป็น 3)
    if not st.session_state.is_member and st.session_state.usage_count >= 3:
        st.warning("คุณใช้สิทธิ์ฟรีครบ 3 ครั้งแล้ว กรุณาอัปเกรดเป็นสมาชิกเพื่อใช้งานต่อ")
        return

    with st.spinner("กำลังวิเคราะห์ด้วย AI..."):
        try:
            prompt = "วิเคราะห์ภาพก่อสร้างและตอบเป็น JSON ตามโครงสร้างเดิม..."
            img_inp = Image.open(site) if site else Image.open(bp)
            res = st.session_state.engine.generate_content([prompt, img_inp], generation_config={"response_mime_type": "application/json"})
            st.session_state.json_data = json.loads(res.text)
            st.session_state.usage_count += 1 # นับการใช้งาน
        except Exception as e: st.error(f"Analysis Error: {e}")

if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 7. DISPLAY RESULTS (ใช้ UI V4 เดิมของคุณ) ---
if st.session_state.json_data:
    # ... (ส่วนการแสดงผล Shopping List และ Defect ต่างๆ เหมือนโค้ดเดิมเป๊ะ) ...
    st.success(f"วิเคราะห์สำเร็จ (ใช้ไปแล้ว {st.session_state.usage_count}/3 ครั้ง)")

st.markdown("<div style='text-align:center; margin-top:50px; color:#4A3F35; font-size:0.7rem;'>BHOON KHARN | PRIVATE SYSTEM</div>", unsafe_allow_html=True)
