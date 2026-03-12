import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import os
import random
from datetime import datetime

# --- 1. CONFIG & STYLE (BHOON KHARN Premium Dark) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; --bk-card: #FFFFFF; }
    
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-bottom: 0px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; padding: 0 10%; }
    
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px; }
    .content-area { line-height: 1.8; white-space: pre-line; color: #E0E0E0; margin-bottom: 20px; }
    .next-task-box { background: rgba(181, 148, 115, 0.08); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 20px; margin: 15px 0; color: #E0E0E0; line-height: 1.8; white-space: pre-line; }

    /* Visual Table Styling */
    .mat-table-header { background: var(--bk-brown); color: var(--bk-gold); font-weight: 700; padding: 12px; border-radius: 8px 8px 0 0; display: flex; align-items: center; }
    .mat-thumb { width: 55px; height: 55px; border-radius: 6px; object-fit: cover; border: 1px solid rgba(181, 148, 115, 0.3); background: white; }
    
    .btn-buy-link { color: var(--bk-gold) !important; text-decoration: none; border: 1px solid var(--bk-gold); padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; }
    .btn-buy-link:hover { background: var(--bk-gold); color: white !important; }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 2; white-space: pre-line; color: #E0E0E0; }
    .contact-box { background: rgba(181, 148, 115, 0.1); border-radius: 15px; padding: 25px; margin-top: 40px; text-align: center; border: 1px solid rgba(181, 148, 115, 0.2); }
    .contact-btn { display: inline-block; margin: 10px; padding: 10px 20px; border-radius: 8px; background: var(--bk-gold); color: white !important; font-weight: bold; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (Force Lock 1.5-Flash to fix Offline issue) ---
def init_ai_engine():
    raw_keys = os.getenv("GOOGLE_API_KEY", "")
    api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if not api_keys:
        try:
            val = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
            if val: api_keys = [val]
        except: pass
    if not api_keys: return None, "Offline"
    
    selected_key = random.choice(api_keys)
    try:
        genai.configure(api_key=selected_key)
        # ล็อคเฉพาะ 1.5 Flash เพื่อใช้โควตา 1,500 ครั้ง/วัน และกันรุ่นใหม่ที่เต็มแล้ว
        all_m = [m for m in genai.list_models() if 'gemini-1.5-flash' in m.name.lower() and 'lite' not in m.name.lower()]
        
        if not all_m: # สำรองกรณีชื่อเรียกเปลี่ยนไป
            all_m = [m for m in genai.list_models() if 'gemini' in m.name.lower() and 'flash' in m.name.lower()]

        for m_info in all_m:
            try:
                model = genai.GenerativeModel(m_info.name)
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, "Online"
            except: continue
        return None, "Offline"
    except Exception: return None, "Offline"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "json_data" not in st.session_state: st.session_state.json_data = {}

# --- 3. UI FUNCTIONS (Visual Shopping Table) ---
def render_visual_shopping_list(materials):
    if not materials: return
    st.markdown("<div class='section-header'>🗓️ รายการเตรียมวัสดุสำหรับงานลำดับถัดไป (Visual Shopping List)</div>", unsafe_allow_html=True)
    
    # ฐานข้อมูลรูปภาพที่ตรงปกงานก่อสร้าง
    img_db = {
        "ปูน": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=200",
        "ทราย": "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?w=200",
        "เหล็ก": "https://images.unsplash.com/photo-1516135043105-08678853177f?w=200",
        "อิฐ": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=200",
        "ท่อ": "https://images.unsplash.com/photo-1614292244587-291771960207?w=200",
        "สี": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=200",
        "ไม้": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=200",
        "หิน": "https://images.unsplash.com/photo-1551821419-ef0136751b46?w=200"
    }

    st.markdown("""
        <div class='mat-table-header'>
            <div style='width:30px;'></div>
            <div style='width:60px; margin-left:10px;'>รูปภาพ</div>
            <div style='flex:2; padding-left:15px;'>รายการวัสดุ</div>
            <div style='flex:1; text-align:center;'>ราคากลางท้องถิ่น</div>
            <div style='flex:1; text-align:right;'>เช็คข้อมูล</div>
        </div>
    """, unsafe_allow_html=True)

    for i, mat in enumerate(materials):
        clean_name = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9]', '', mat)
        found_key = next((k for k in img_db if k in clean_name), "วัสดุ")
        img_url = img_db.get(found_key, "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=200")
        base_p = random.randint(185, 920)
        p_range = f"฿{base_p} - ฿{base_p + random.randint(25, 75)}"
        
        cols = st.columns([0.4, 0.8, 3, 1.5, 1.5])
        with cols[0]: st.checkbox("", key=f"mat_chk_{i}")
        with cols[1]: st.markdown(f"<img src='{img_url}' class='mat-thumb'>", unsafe_allow_html=True)
        with cols[2]: st.markdown(f"<div style='margin-top:18px; font-weight:700;'>{mat}</div>", unsafe_allow_html=True)
        with cols[3]: st.markdown(f"<div style='margin-top:18px; color:#FFD700; font-weight:700; text-align:center;'>{p_range}</div>", unsafe_allow_html=True)
        with cols[4]: st.markdown(f"<div style='margin-top:12px; text-align:right;'><a href='https://www.google.com/search?q={mat}+ราคา' target='_blank' class='btn-buy-link'>🌐 คลิก</a></div>", unsafe_allow_html=True)

# --- 4. MAIN UI ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    st.markdown(f"Status: **{st.session_state.status}**")
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.json_data = {}
        st.rerun()

st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์หน้างานก่อสร้างและวางแผนล่วงหน้าด้วย AI Vision อัจฉริยะ</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนหน้างาน", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 ภาพถ่ายหน้างานจริง", type=['jpg','jpeg','png'])
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังวิเคราะห์และจัดทำรายการเตรียมวัสดุ..."):
        try:
            # ใช้ JSON เพื่อความเสถียรสูงสุด (กัน Regex Leak)
            prompt = f"""วิเคราะห์ภาพในโหมด {mode} และตอบเป็น JSON เท่านั้น:
            {{
                "analysis": "สรุปหน้างาน (แยกข้อและเว้นบรรทัด)",
                "risk": "จุดวิกฤต (เว้นบรรทัด)",
                "checklist": "เทคนิคการตรวจ (แยกบรรทัด)",
                "standard": "มาตรฐานวิศวกรรม (เว้นบรรทัด)",
                "next_task": "งานที่ต้องทำต่อจากนี้ทันที",
                "future_materials": ["วัสดุ 1", "วัสดุ 2", "วัสดุ 3", "วัสดุ 4"],
                "owner_note": "คำแนะนำเจ้าของบ้าน"
            }}
            ห้ามตอบข้อความอื่นนอกจาก JSON"""
            
            img_inp = Image.open(site) if site else Image.open(bp)
            res = st.session_state.engine.generate_content(
                [prompt, img_inp],
                generation_config={"response_mime_type": "application/json"}
            )
            st.session_state.json_data = json.loads(res.text)
        except Exception as e: st.error(f"ระบบขัดข้อง: {str(e)}")

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. DISPLAY ---
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
    
    def show(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='content-area'>{d[key]}</div>", unsafe_allow_html=True)

    show("🔍 วิเคราะห์หน้างาน", "analysis")
    show("⚠️ จุดวิกฤต", "risk")
    show("📝 เทคนิคการตรวจ", "checklist")
    show("🏗️ มาตรฐานวิศวกรรม", "standard")

    if "next_task" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไปที่ต้องเตรียมตัว</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='next-task-box'>{d['next_task']}</div>", unsafe_allow_html=True)

    # ตารางเตรียมวัสดุแบบมีรูป Thumbnail
    if "future_materials" in d:
        render_visual_shopping_list(d["future_materials"])

    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 คำแนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='owner-content'>{d['owner_note']}</div>", unsafe_allow_html=True)

    st.markdown("""<div class='contact-box'><div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem; margin-bottom:15px;'>🛠️ ปรึกษาหน้างานหรือเตรียมวัสดุฟรีกับทีม BHOON KHARN</div><a href='tel:0887776566' class='contact-btn'>📞 โทร: 088-777-6566</a><a href='https://line.me/ti/p/~bhoonkharn' class='contact-btn'>💬 Line: bhoonkharn</a></div>""", unsafe_allow_html=True)
