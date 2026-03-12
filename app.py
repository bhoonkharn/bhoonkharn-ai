import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import os
import random

# --- 1. CONFIG & STYLE (BHOON KHARN Premium V4 - Neutral Edition) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; }
    
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-bottom: 0px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; padding: 0 10%; }
    
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px; }
    
    /* Formatting for List */
    .content-list { line-height: 2; color: #E0E0E0; margin-bottom: 20px; list-style-type: none; padding-left: 0; }
    .content-list li { margin-bottom: 10px; padding-left: 25px; position: relative; }
    .content-list li::before { content: "•"; color: var(--bk-gold); position: absolute; left: 0; font-weight: bold; }
    
    .next-task-box { background: rgba(181, 148, 115, 0.08); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 20px; margin: 15px 0; color: #E0E0E0; line-height: 1.8; }

    /* Neutral Shopping Table V4 */
    .mat-table-header { background: var(--bk-brown); color: var(--bk-gold); font-weight: 700; padding: 15px; border-radius: 10px 10px 0 0; display: flex; align-items: center; }
    .mat-thumb-v4 { width: 150px; height: 150px; border-radius: 12px; object-fit: cover; border: 2px solid rgba(181, 148, 115, 0.4); background: #2A2420; margin: 10px 0; }
    
    .btn-search-link { color: var(--bk-gold) !important; text-decoration: none; border: 1px solid var(--bk-gold); padding: 8px 18px; border-radius: 8px; font-size: 0.85rem; font-weight: bold; }
    .btn-search-link:hover { background: var(--bk-gold); color: white !important; }

    .owner-box { border-left: 5px solid var(--bk-gold); padding: 20px; background: rgba(181, 148, 115, 0.07); border-radius: 0 15px 15px 0; margin: 25px 0; }
    .contact-box { background: rgba(181, 148, 115, 0.1); border-radius: 15px; padding: 25px; margin-top: 40px; text-align: center; border: 1px solid rgba(181, 148, 115, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (Stable Multi-Key Picker) ---
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
            if "2.5" in n or "3" in n or "preview" in n or "lite" in n: return 99
            if "1.5-flash" in n: return 1
            return 10
        
        all_m.sort(key=lambda x: quota_safe_score(x.name))

        for m_info in all_m:
            if quota_safe_score(m_info.name) < 90:
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

# --- 3. UI FUNCTIONS (Neutral Iconography) ---
def render_neutral_shopping_list(materials_data):
    if not materials_data: return
    st.markdown("<div class='section-header'>🗓️ รายการเตรียมวัสดุ (Neutral Shopping List)</div>", unsafe_allow_html=True)
    
    # ฐานข้อมูลรูปภาพเชิงสัญลักษณ์หน้างาน (เป็นกลาง ไม่มียี่ห้อ)
    context_img = {
        "ปูน": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500",
        "ทราย": "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?w=500",
        "เหล็ก": "https://images.unsplash.com/photo-1516135043105-08678853177f?w=500",
        "อิฐ": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500",
        "ท่อ": "https://images.unsplash.com/photo-1614292244587-291771960207?w=500",
        "สี": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=500",
        "ไม้": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500",
        "กระเบื้อง": "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=500",
        "สายไฟ": "https://images.unsplash.com/photo-1558444479-c8f01052877a?w=500",
        "งานดิน": "https://images.unsplash.com/photo-1541888946425-d81bb19480c5?w=500"
    }

    st.markdown("""
        <div class='mat-table-header'>
            <div style='width:40px;'></div>
            <div style='width:160px; margin-left:10px;'>ประเภทวัสดุ</div>
            <div style='flex:3; padding-left:30px;'>สเปกและรายการที่แนะนำ</div>
            <div style='flex:1.5; text-align:center;'>ราคากลางตลาด</div>
            <div style='flex:1.2; text-align:right;'>เลือกยี่ห้อ</div>
        </div>
    """, unsafe_allow_html=True)

    for i, item in enumerate(materials_data):
        name = item.get("name", "วัสดุก่อสร้าง")
        price = item.get("price", "฿0 - ฿0")
        keyword = item.get("img_keyword", "วัสดุ").lower()
        
        found_key = next((k for k in context_img if k in keyword or k in name.lower()), "งานดิน")
        img_url = context_img.get(found_key)
        
        cols = st.columns([0.4, 1.6, 3, 1.5, 1.2])
        with cols[0]: st.checkbox("", key=f"mat_neu_{i}")
        with cols[1]: st.markdown(f"<img src='{img_url}' class='mat-thumb-v4'>", unsafe_allow_html=True)
        with cols[2]: st.markdown(f"<div style='margin-top:45px; font-weight:700; font-size:1.1rem;'>{name}</div><div style='color:#A09080; font-size:0.85rem;'>ระบุสเปกเพื่อความเป็นกลางในการเลือกซื้อ</div>", unsafe_allow_html=True)
        with cols[3]: st.markdown(f"<div style='margin-top:55px; color:#FFD700; font-weight:700; font-size:1.15rem; text-align:center;'>{price}</div>", unsafe_allow_html=True)
        with cols[4]: st.markdown(f"<div style='margin-top:50px; text-align:right;'><a href='https://www.google.com/search?q={name}+ราคา+ร้านวัสดุ' target='_blank' class='btn-search-link'>🌐 ค้นหา</a></div>", unsafe_allow_html=True)

# --- 4. MAIN UI ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    st.markdown(f"Status: **{st.session_state.status}**")
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติหน้างาน", use_container_width=True):
        st.session_state.json_data = {}
        st.rerun()

st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์หน้างานก่อสร้างด้วย AI Vision อัจฉริยะ (Professional Neutral Edition)</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนหน้างาน", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 ภาพถ่ายหน้างานจริง", type=['jpg','jpeg','png'])
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังวิเคราะห์สเปกวัสดุแบบเป็นกลาง..."):
        try:
            prompt = f"""ในฐานะ BHOON KHARN AI โหมด {mode} ให้วิเคราะห์ภาพและตอบเป็น JSON เท่านั้น:
            {{
                "analysis": ["สรุปข้อที่ 1", "สรุปข้อที่ 2"],
                "risk": ["จุดเสี่ยง 1", "จุดเสี่ยง 2"],
                "checklist": ["เทคนิคตรวจ 1", "เทคนิคตรวจ 2"],
                "standard": ["มาตรฐาน 1", "มาตรฐาน 2"],
                "next_task": "งานลำดับถัดไป (ระบุงานจริง 1 ประโยค)",
                "future_materials": [
                    {{"name": "สเปกวัสดุ 1 (ระบุรุ่นมาตรฐานห้ามเจาะจงยี่ห้อ)", "price": "฿-฿", "img_keyword": "ปูน"}},
                    {{"name": "สเปกวัสดุ 2 (ระบุรุ่นมาตรฐานห้ามเจาะจงยี่ห้อ)", "price": "฿-฿", "img_keyword": "เหล็ก"}},
                    {{"name": "สเปกวัสดุ 3 (ระบุรุ่นมาตรฐานห้ามเจาะจงยี่ห้อ)", "price": "฿-฿", "img_keyword": "ท่อ"}}
                ],
                "owner_note": ["คำแนะนำ 1", "คำแนะนำ 2"]
            }}
            ห้ามตอบนอกเหนือจาก JSON ห้ามระบุยี่ห้อสินค้าให้ระบุเป็นชื่อเรียกมาตรฐานวัสดุเท่านั้น"""
            
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

# --- 5. DISPLAY (Stable Rendering) ---
if st.session_state.json_data:
    d = st.session_state.json_data
    st.divider()
    
    def render_section_v4(title, key):
        if key in d:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            items = d[key]
            if isinstance(items, list):
                list_html = "<ul class='content-list'>" + "".join([f"<li>{i}</li>" for i in items]) + "</ul>"
                st.markdown(list_html, unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='line-height:1.8; margin-bottom:20px;'>{items}</div>", unsafe_allow_html=True)

    render_section_v4("🔍 วิเคราะห์หน้างาน", "analysis")
    render_section_v4("⚠️ จุดวิกฤตที่ต้องระวัง", "risk")
    render_section_v4("📝 เทคนิคการตรวจงานแบบละเอียด", "checklist")
    render_section_v4("🏗️ มาตรฐานวิศวกรรมที่เกี่ยวข้อง", "standard")

    if "next_task" in d:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไปที่ต้องเตรียมตัว</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='next-task-box'>{d['next_task']}</div>", unsafe_allow_html=True)

    # ตารางแบบเป็นกลาง (Neutral Visuals)
    if "future_materials" in d:
        render_neutral_shopping_list(d["future_materials"])

    if "owner_note" in d:
        st.markdown("<div class='section-header'>🏠 คำแนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        items = d["owner_note"]
        if isinstance(items, list):
            list_html = "<div class='owner-box'><ul class='content-list' style='margin-bottom:0;'>" + "".join([f"<li>{i}</li>" for i in items]) + "</ul></div>"
            st.markdown(list_html, unsafe_allow_html=True)

    st.markdown("""<div class='contact-box'><div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem; margin-bottom:15px;'>🛠️ ปรึกษาหน้างานหรือเตรียมวัสดุฟรีกับทีม BHOON KHARN</div><div style='font-size:0.9rem; color:#A09080; margin-bottom:15px;'>โทร: 088-777-6566 | Line: bhoonkharn</div></div>""", unsafe_allow_html=True)
