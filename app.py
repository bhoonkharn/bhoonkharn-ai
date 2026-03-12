import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import os
import random
from datetime import datetime

# --- 1. CONFIG & STYLE (Premium BHOON KHARN V3-XL) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; --bk-card: #FFFFFF; }
    
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-bottom: 0px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; padding: 0 10%; }
    
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px; }
    
    /* Perfect Line Breaks Style */
    .content-list { line-height: 2; color: #E0E0E0; margin-bottom: 20px; list-style-type: none; padding-left: 0; }
    .content-list li { margin-bottom: 10px; padding-left: 25px; position: relative; }
    .content-list li::before { content: "•"; color: var(--bk-gold); position: absolute; left: 0; font-weight: bold; }
    
    .next-task-box { background: rgba(181, 148, 115, 0.08); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 20px; margin: 15px 0; color: #E0E0E0; line-height: 1.8; }

    /* Visual Table XL (150px) */
    .mat-table-header { background: var(--bk-brown); color: var(--bk-gold); font-weight: 700; padding: 15px; border-radius: 10px 10px 0 0; display: flex; align-items: center; }
    .mat-thumb-xl { width: 150px; height: 150px; border-radius: 12px; object-fit: cover; border: 2px solid rgba(181, 148, 115, 0.4); background: white; margin: 10px 0; }
    
    .btn-check-link { color: var(--bk-gold) !important; text-decoration: none; border: 1px solid var(--bk-gold); padding: 8px 18px; border-radius: 8px; font-size: 0.9rem; font-weight: bold; }
    .btn-check-link:hover { background: var(--bk-gold); color: white !important; }

    .owner-box { border-left: 5px solid var(--bk-gold); padding: 20px; background: rgba(181, 148, 115, 0.07); border-radius: 0 15px 15px 0; margin: 25px 0; }
    .contact-box { background: rgba(181, 148, 115, 0.1); border-radius: 15px; padding: 25px; margin-top: 40px; text-align: center; border: 1px solid rgba(181, 148, 115, 0.2); }
    .contact-btn { display: inline-block; margin: 10px; padding: 10px 20px; border-radius: 8px; background: var(--bk-gold); color: white !important; font-weight: bold; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (The Original Template 3 Logic - High Stability) ---
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
        all_m = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()]
        
        def quota_safe_score(name):
            n = name.lower()
            if "2.5" in n or "3" in n or "preview" in n or "robotics" in n: return 99
            if "1.5-flash" in n: return 1
            if "1.5-pro" in n: return 2
            return 10
        
        all_m.sort(key=lambda x: quota_safe_score(x.name))

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

# --- 3. UI FUNCTIONS (Updated to Smart Web-Proxy Search) ---
def render_text_materials_summary(materials_data, next_task):
    st.markdown("<div class='section-header'>📋 แผนการเตรียมวัสดุ (สรุปเนื้อหา)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='next-task-box'><b>งานปัจจุบัน/ลำดับถัดไป:</b> {next_task}</div>", unsafe_allow_html=True)
    
    if materials_data:
        st.markdown("<p style='color:var(--bk-gold); font-weight:bold;'>รายการวัสดุทั้งหมดที่ต้องเตรียม:</p>", unsafe_allow_html=True)
        mat_list_text = "".join([f"<li>{m['name']} ({m.get('price', 'เช็คราคา')})</li>" for m in materials_data])
        st.markdown(f"<ul class='content-list'>{mat_list_text}</ul>", unsafe_allow_html=True)

def render_random_visual_showcase(materials_data):
    if not materials_data: return
    
    # สุ่มเลือกมา 3-5 รายการ
    count = random.randint(3, 5)
    selected_mats = random.sample(materials_data, min(len(materials_data), count))
    
    st.markdown("<div class='section-header'>🏗️ รายการแนะนำวัสดุ (Smart Search 3-5 รายการ)</div>", unsafe_allow_html=True)
    
    # ระบบ Keyword Mapping สำหรับ Smart Web-Proxy
    mat_keywords = {
        "ปูน": "cement", "ทราย": "sand", "เหล็ก": "rebar", "อิฐ": "bricks",
        "ท่อ": "pipes", "สี": "paint", "กระเบื้อง": "tiles", "สายไฟ": "electric",
        "ไม้": "wood", "หิน": "gravel"
    }

    st.markdown("""
        <div class='mat-table-header'>
            <div style='width:40px;'></div>
            <div style='width:160px; margin-left:10px;'>รูปภาพวัสดุ</div>
            <div style='flex:3; padding-left:30px;'>ชื่อรุ่นและสเปกแนะนำ</div>
            <div style='flex:1.5; text-align:center;'>ราคากลางท้องถิ่น</div>
            <div style='flex:1.2; text-align:right;'>เช็คข้อมูล</div>
        </div>
    """, unsafe_allow_html=True)

    for i, item in enumerate(selected_mats):
        name = item.get("name", "วัสดุก่อสร้าง")
        price = item.get("price", "฿0 - ฿0")
        keyword = item.get("img_keyword", "วัสดุ").lower()
        
        # ค้นหาคีย์เวิร์ดที่ตรงที่สุดเพื่อทำ Smart Search
        found_tag = next((mat_keywords[k] for k in mat_keywords if k in keyword or k in name.lower()), "construction")
        
        # Option 3: Smart Web-Proxy Search (Featured)
        img_url = f"https://source.unsplash.com/featured/300x300?construction,{found_tag}"
        
        cols = st.columns([0.4, 1.6, 3, 1.5, 1.2])
        with cols[0]: st.checkbox("", key=f"mat_rand_{i}")
        with cols[1]: st.markdown(f"<img src='{img_url}' class='mat-thumb-xl'>", unsafe_allow_html=True)
        with cols[2]: st.markdown(f"<div style='margin-top:45px; font-weight:700; font-size:1.15rem;'>{name}</div><div style='color:#A09080; font-size:0.9rem;'>รุ่นที่แนะนำตามสเปกหน้างาน</div>", unsafe_allow_html=True)
        with cols[3]: st.markdown(f"<div style='margin-top:55px; color:#FFD700; font-weight:700; font-size:1.15rem; text-align:center;'>{price}</div>", unsafe_allow_html=True)
        with cols[4]: st.markdown(f"<div style='margin-top:50px; text-align:right;'><a href='https://www.google.com/search?q={name}+ราคา' target='_blank' class='btn-check-link'>🌐 คลิก</a></div>", unsafe_allow_html=True)

# --- 4. MAIN UI (Everything else remains untouched) ---
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
    with st.spinner("AI กำลังวิเคราะห์และจัดเตรียมข้อมูล..."):
        try:
            prompt = f"""ในฐานะ BHOON KHARN AI โหมด {mode} ให้วิเคราะห์ภาพและตอบเป็น JSON เท่านั้น:
            {{
                "analysis": ["สรุปข้อ 1", "สรุปข้อ 2"],
                "risk": ["จุดเสี่ยง 1", "จุดเสี่ยง 2"],
                "checklist": ["เทคนิคตรวจ 1", "เทคนิคตรวจ 2"],
                "standard": ["มาตรฐาน 1", "มาตรฐาน 2"],
                "next_task": "งานที่ต้องทำต่อทันที",
                "future_materials": [
                    {{"name": "ระบุรุ่น/ยี่ห้อวัสดุ 1", "price": "฿-฿", "img_keyword": "ปูน"}},
                    {{"name": "ระบุรุ่น/ยี่ห้อวัสดุ 2", "price": "฿-฿", "img_keyword": "เหล็ก"}},
                    {{"name": "ระบุรุ่น/ยี่ห้อวัสดุ 3", "price": "฿-฿", "img_keyword": "ท่อ"}}
                ],
                "owner_note": ["คำแนะนำ 1", "คำแนะนำ 2"]
            }}
            ห้ามตอบนอกเหนือจาก JSON และข้อมูลใน [] ต้องแยกเป็นข้อๆ เสมอ"""
            
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
    
    def show_list_section(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            items = d[key]
            if isinstance(items, list):
                list_html = "<ul class='content-list'>" + "".join([f"<li>{i}</li>" for i in items]) + "</ul>"
                st.markdown(list_html, unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='margin-bottom:20px;'>{items}</div>", unsafe_allow_html=True)

    show_list_section("🔍 วิเคราะห์หน้างาน", "analysis")
    show_list_section("⚠️ จุดวิกฤตที่ต้องระวัง", "risk")
    show_list_section("📝 เทคนิคการตรวจงานแบบละเอียด", "checklist")
    show_list_section("🏗️ มาตรฐานวิศวกรรมที่เกี่ยวข้อง", "standard")

    if "future_materials" in d:
        render_text_materials_summary(d["future_materials"], d.get("next_task", "งานลำดับถัดไป"))
        render_random_visual_showcase(d["future_materials"])

    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 คำแนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        items = d["owner_note"]
        if isinstance(items, list):
            list_html = "<div class='owner-box'><ul class='content-list' style='margin-bottom:0;'>" + "".join([f"<li>{i}</li>" for i in items]) + "</ul></div>"
            st.markdown(list_html, unsafe_allow_html=True)

    st.markdown("""<div class='contact-box'><div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem; margin-bottom:15px;'>🛠️ ปรึกษาหน้างานหรือเตรียมวัสดุฟรีกับทีม BHOON KHARN</div><a href='tel:0887776566' class='contact-btn'>📞 โทร: 088-777-6566</a><a href='https://line.me/ti/p/~bhoonkharn' class='contact-btn'>💬 Line: bhoonkharn</a></div>""", unsafe_allow_html=True)
