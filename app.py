import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import os
import random
from datetime import datetime

# --- 1. CONFIG & STYLE (BHOON KHARN Premium Dark V2) ---
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

    /* Shopping Table V2 (Bigger & Clearer) */
    .mat-table-header { background: var(--bk-brown); color: var(--bk-gold); font-weight: 700; padding: 15px; border-radius: 10px 10px 0 0; display: flex; align-items: center; }
    .mat-thumb-lg { width: 130px; height: 130px; border-radius: 10px; object-fit: cover; border: 2px solid rgba(181, 148, 115, 0.3); background: white; margin: 10px 0; }
    
    .mat-row-v2 { border-bottom: 1px solid rgba(181, 148, 115, 0.1); padding: 15px 0; }
    .btn-check-link { color: var(--bk-gold) !important; text-decoration: none; border: 1px solid var(--bk-gold); padding: 6px 15px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; }
    .btn-check-link:hover { background: var(--bk-gold); color: white !important; }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 2; white-space: pre-line; color: #E0E0E0; }
    .contact-box { background: rgba(181, 148, 115, 0.1); border-radius: 15px; padding: 25px; margin-top: 40px; text-align: center; border: 1px solid rgba(181, 148, 115, 0.2); }
    .contact-btn { display: inline-block; margin: 10px; padding: 10px 20px; border-radius: 8px; background: var(--bk-gold); color: white !important; font-weight: bold; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (Force Gemini 1.5 Flash for Max Quota) ---
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
        # เจาะจงใช้รุ่น 1.5-flash เพื่อเลี่ยง Error 429
        all_m = [m for m in genai.list_models() if 'gemini-1.5-flash' in m.name.lower() and 'lite' not in m.name.lower()]
        if not all_m: all_m = [m for m in genai.list_models() if 'gemini' in m.name.lower()]

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

# --- 3. UI FUNCTIONS (Visual Shopping V2) ---
def render_visual_shopping_v2(materials_data):
    if not materials_data: return
    st.markdown("<div class='section-header'>🗓️ รายการเตรียมวัสดุสำหรับงานลำดับถัดไป (Shopping List V2)</div>", unsafe_allow_html=True)
    
    # ฐานข้อมูลรูปภาพวัสดุจริง
    img_db = {
        "ปูน": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400",
        "ทราย": "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?w=400",
        "เหล็ก": "https://images.unsplash.com/photo-1516135043105-08678853177f?w=400",
        "อิฐ": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400",
        "หิน": "https://images.unsplash.com/photo-1551821419-ef0136751b46?w=400",
        "ท่อ": "https://images.unsplash.com/photo-1614292244587-291771960207?w=400",
        "สี": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400",
        "ไม้": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=400",
        "กระเบื้อง": "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=400",
        "สายไฟ": "https://images.unsplash.com/photo-1558444479-c8f01052877a?w=400",
        "น้ำยา": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400"
    }

    st.markdown("""
        <div class='mat-table-header'>
            <div style='width:40px;'></div>
            <div style='width:140px; margin-left:10px;'>รูปภาพวัสดุ</div>
            <div style='flex:3; padding-left:25px;'>รายการและสเปกที่แนะนำ</div>
            <div style='flex:1.5; text-align:center;'>ราคากลางท้องถิ่น</div>
            <div style='flex:1.2; text-align:right;'>ข้อมูลสเปก</div>
        </div>
    """, unsafe_allow_html=True)

    for i, item in enumerate(materials_data):
        name = item.get("name", "วัสดุก่อสร้าง")
        price = item.get("price", "฿0 - ฿0")
        keyword = item.get("img_keyword", "วัสดุ")
        
        # Mapping รูปภาพ
        found_key = next((k for k in img_db if k in keyword or k in name), "วัสดุ")
        img_url = img_db.get(found_key, "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400")
        
        cols = st.columns([0.4, 1.4, 3, 1.5, 1.2])
        with cols[0]: st.checkbox("", key=f"mat_v2_{i}")
        with cols[1]: st.markdown(f"<img src='{img_url}' class='mat-thumb-lg'>", unsafe_allow_html=True)
        with cols[2]: st.markdown(f"<div style='margin-top:35px; font-weight:700; font-size:1.1rem;'>{name}</div><div style='color:#888; font-size:0.85rem;'>สเปกแนะนำสำหรับงานขั้นตอนนี้</div>", unsafe_allow_html=True)
        with cols[3]: st.markdown(f"<div style='margin-top:45px; color:#FFD700; font-weight:700; font-size:1.1rem; text-align:center;'>{price}</div>", unsafe_allow_html=True)
        with cols[4]: st.markdown(f"<div style='margin-top:42px; text-align:right;'><a href='https://www.google.com/search?q={name}+สเปก+ราคา' target='_blank' class='btn-check-link'>🌐 เช็คสเปก</a></div>", unsafe_allow_html=True)

# --- 4. MAIN UI ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    st.markdown(f"Status: **{st.session_state.status}**")
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติหน้างาน", use_container_width=True):
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
    with st.spinner("AI กำลังวิเคราะห์สเปกวัสดุและคำนวณราคา..."):
        try:
            # สั่ง AI ให้ระบุยี่ห้อและราคากลางที่สมจริง
            prompt = f"""ในฐานะ BHOON KHARN AI โหมด {mode} ให้วิเคราะห์ภาพและตอบเป็น JSON เท่านั้น:
            {{
                "analysis": "สรุปหน้างานปัจจุบัน (แยกข้อ)",
                "risk": "จุดวิกฤตที่ต้องระวัง (แยกข้อ)",
                "checklist": "เทคนิคการตรวจงานแบบละเอียด",
                "standard": "มาตรฐานวิศวกรรมที่เกี่ยวข้อง",
                "next_task": "งานลำดับถัดไปที่จะเกิดขึ้นจริง",
                "future_materials": [
                    {{"name": "ชื่อรุ่น/ยี่ห้อวัสดุยอดนิยม 1", "price": "ช่วงราคากลาง ฿-฿", "img_keyword": "ปูน"}},
                    {{"name": "ชื่อรุ่น/ยี่ห้อวัสดุยอดนิยม 2", "price": "ช่วงราคากลาง ฿-฿", "img_keyword": "เหล็ก"}},
                    {{"name": "ชื่อรุ่น/ยี่ห้อวัสดุยอดนิยม 3", "price": "ช่วงราคากลาง ฿-฿", "img_keyword": "ท่อ"}},
                    {{"name": "ชื่อรุ่น/ยี่ห้อวัสดุยอดนิยม 4", "price": "ช่วงราคากลาง ฿-฿", "img_keyword": "ทราย"}}
                ],
                "owner_note": "แนะนำพิเศษสำหรับเจ้าของบ้าน"
            }}
            ห้ามใช้ข้อความสุ่ม ให้ใช้ข้อมูลจริงจากมาตรฐานงานช่างในไทย"""
            
            img_inp = Image.open(site) if site else Image.open(bp)
            res = st.session_state.engine.generate_content(
                [prompt, img_inp],
                generation_config={"response_mime_type": "application/json"}
            )
            st.session_state.json_data = json.loads(res.text)
        except Exception as e: st.error(f"ระบบขัดข้อง: {str(e)}")

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพหน้างาน")

# --- 5. DISPLAY ---
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
    
    def show_v2(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='content-area'>{d[key]}</div>", unsafe_allow_html=True)

    show_v2("🔍 วิเคราะห์หน้างาน", "analysis")
    show_v2("⚠️ จุดวิกฤต", "risk")
    show_v2("📝 เทคนิคการตรวจ", "checklist")
    show_v2("🏗️ มาตรฐานวิศวกรรม", "standard")

    if "next_task" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไปที่ต้องเตรียมตัว</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='next-task-box'>{d['next_task']}</div>", unsafe_allow_html=True)

    # ตารางเตรียมวัสดุแบบ V2 (รูปใหญ่ + รุ่นสินค้า)
    if "future_materials" in d:
        render_visual_shopping_v2(d["future_materials"])

    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 คำแนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='owner-content'>{d['owner_note']}</div>", unsafe_allow_html=True)

    st.markdown("""<div class='contact-box'><div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem; margin-bottom:15px;'>🛠️ ปรึกษาหน้างานหรือเตรียมวัสดุฟรีกับทีม BHOON KHARN</div><a href='tel:0887776566' class='contact-btn'>📞 โทร: 088-777-6566</a><a href='https://line.me/ti/p/~bhoonkharn' class='contact-btn'>💬 Line: bhoonkharn</a></div>""", unsafe_allow_html=True)
