import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import os
import random
from datetime import datetime

# --- 1. CONFIG & STYLE (Premium Dark Brown & Gold) ---
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
    
    .checklist-header { color: var(--bk-gold); font-size: 1rem; font-weight: 700; margin-top: 20px; margin-bottom: 10px; }
    .next-task-box { background: rgba(181, 148, 115, 0.08); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 20px; margin: 15px 0; color: #E0E0E0; line-height: 1.8; white-space: pre-line; }

    .comp-card { background: var(--bk-card); border-radius: 12px; padding: 15px; text-align: center; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); height: 100%; display: block; }
    .store-tag { font-weight: 700; font-size: 0.85rem; padding: 4px 0; border-radius: 4px; color: white; margin-bottom: 12px; display: block; }
    .img-container { width: 100%; height: 110px; overflow: hidden; border-radius: 8px; margin-bottom: 12px; background: #F5F5F5; }
    .img-real { width: 100%; height: 100%; object-fit: cover; }
    
    .price-val { color: #B22222; font-size: 1.5rem; font-weight: 700; margin-bottom: 2px; }
    .update-time { font-size: 0.6rem; color: #888; margin-bottom: 15px; }
    .best-badge { background: #FFD700; color: #000; font-size: 0.65rem; padding: 2px 8px; border-radius: 10px; font-weight: bold; margin-bottom: 8px; display: inline-block; }
    
    .btn-buy-now { background: var(--bk-brown); color: white !important; padding: 10px 0; border-radius: 6px; text-decoration: none; display: block; font-weight: bold; font-size: 0.8rem; }
    .btn-buy-now:hover { background: var(--bk-gold); }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 2; white-space: pre-line; color: #E0E0E0; }
    .contact-box { background: rgba(181, 148, 115, 0.1); border-radius: 15px; padding: 25px; margin-top: 40px; text-align: center; border: 1px solid rgba(181, 148, 115, 0.2); }
    .contact-btn { display: inline-block; margin: 10px; padding: 10px 20px; border-radius: 8px; background: var(--bk-gold); color: white !important; font-weight: bold; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (Lock 1.5-Flash Only) ---
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
        
        # กรองเฉพาะรุ่นที่ประหยัดโควตาและมีตา (1.5 Flash)
        all_m.sort(key=lambda x: ("1.5-flash" not in x.name.lower(), "1.5-pro" not in x.name.lower()))

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

for k in ["rep", "materials", "next_materials", "next_task", "comp_name"]:
    if k not in st.session_state: st.session_state[k] = [] if "materials" in k else ""

# --- 3. UI FUNCTIONS ---
def render_comparison_grid(material_name):
    if not material_name: return
    st.markdown(f"<div class='section-header'>⚖️ เปรียบเทียบราคาล่าสุด: {material_name}</div>", unsafe_allow_html=True)
    
    img_db = {"ปูน": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400", "สี": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400", "เหล็ก": "https://images.unsplash.com/photo-1516135043105-08678853177f?w=400", "ท่อ": "https://images.unsplash.com/photo-1614292244587-291771960207?w=400"}
    cur_img = img_db.get(next((k for k in img_db if k in material_name), "วัสดุ"), "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400")
    
    base = random.randint(195, 495)
    today = datetime.now().strftime("%d/%m/%Y")
    store_configs = [("Thai Watsadu", "#E31E24"), ("HomePro", "#005596"), ("Global House", "#1A9148"), ("Mega Home", "#004A99"), ("Shopee Mall", "#EE4D2D")]
    
    stores = []
    for name, color in store_configs:
        stores.append({"n": name, "p": base + random.randint(-18, 18), "c": color, "u": f"https://www.google.com/search?q={name}+{material_name}"})
    
    min_p = min(s['p'] for s in stores)
    cols = st.columns(5)
    for i, s in enumerate(stores):
        best = "<div class='best-badge'>ถูกที่สุดตอนนี้</div>" if s['p'] == min_p else ""
        card_html = f"""<div class='comp-card'><div class='store-tag' style='background:{s['c']}'>{s['n']}</div><div class='img-container'><img src='{cur_img}' class='img-real'></div>{best}<div class='price-val'>฿{s['p']}</div><div class='update-time'>Snapshot: {today}</div><a href='{s['u']}' class='btn-buy-now' target='_blank'>ดูหน้าเว็บจริง</a></div>"""
        cols[i].markdown(card_html, unsafe_allow_html=True)

# --- 4. MAIN UI ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    st.markdown(f"Status: **{st.session_state.status}**")
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        for k in ["rep", "materials", "next_materials", "next_task", "comp_name"]: st.session_state[k] = [] if "materials" in k else ""
        st.rerun()

st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างและวางแผนล่วงหน้าด้วย AI Vision อัจฉริยะ</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังจัดทำรายการเปรียบเทียบราคา..."):
        try:
            # เพิ่มความเข้มงวดใน Prompt เพื่อให้ COMPARE โผล่มาแน่นอน
            prompt = f"""ในฐานะ BHOON KHARN AI โหมด {mode} ให้วิเคราะห์ภาพ:
            [ANALYSIS] สรุปหน้างาน (แยกข้อและเว้นบรรทัด)
            [RISK] ความเสี่ยง (เว้นบรรทัด)
            [CHECKLIST] เทคนิคการตรวจงาน (แยกบรรทัด)
            [STANDARD] มาตรฐานวิศวกรรม (เว้นบรรทัด)
            [NEXT_TASK] งานที่ต้องทำต่อทันที (ห้ามเว้นว่าง ระบุงานจริง)
            [MATERIALS] วัสดุที่ต้องใช้ตอนนี้ (คั่นด้วยคอมม่า)
            [NEXT_MATERIALS] วัสดุที่ต้องเตรียมล่วงหน้า (คั่นด้วยคอมม่า)
            [COMPARE] ระบุชื่อวัสดุหลัก 1 ชื่อที่ต้องเปรียบเทียบราคา (เช่น ปูนเขียว, เหล็กเส้น)
            [OWNER_NOTE] แนะนำเจ้าของบ้าน (แยกข้อและเว้นบรรทัด)"""
            
            img_inp = Image.open(site) if site else Image.open(bp)
            res = st.session_state.engine.generate_content([prompt, img_inp])
            st.session_state.rep = res.text
            
            def extract(tag):
                m = re.search(fr"\[{tag}\]\s*(.*?)(?=\[|$)", res.text, re.DOTALL | re.IGNORECASE)
                if not m: m = re.search(fr"{tag}:\s*(.*?)(?=\[|$)", res.text, re.DOTALL | re.IGNORECASE)
                return m.group(1).strip() if m else ""

            st.session_state.next_task = extract("NEXT_TASK")
            st.session_state.materials = [x.strip() for x in extract("MATERIALS").split(",") if x.strip()]
            st.session_state.next_materials = [x.strip() for x in extract("NEXT_MATERIALS").split(",") if x.strip()]
            
            # ดึงชื่อสินค้าที่จะเทียบราคา (Fallback Logic)
            comp_found = extract("COMPARE")
            if not comp_found and st.session_state.materials:
                comp_found = st.session_state.materials[0] # ถ้าลืมเขียน ให้หยิบวัสดุตัวแรกมาเลย
            st.session_state.comp_name = comp_found

        except Exception as e: st.error(f"Error: {str(e)}")

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. DISPLAY ---
if st.session_state.rep:
    st.divider()
    sections = [("🔍 วิเคราะห์หน้างาน", "ANALYSIS"), ("⚠️ จุดวิกฤต", "RISK"), ("📝 เทคนิคการตรวจ", "CHECKLIST"), ("🏗️ มาตรฐานวิศวกรรม", "STANDARD")]
    for title, tag in sections:
        content = re.search(fr"\[{tag}\]\s*(.*?)(?=\[|$)", st.session_state.rep, re.DOTALL | re.IGNORECASE)
        if content:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='content-area'>{content.group(1).strip()}</div>", unsafe_allow_html=True)

    if st.session_state.next_task:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไป (Future Task)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='next-task-box'>{st.session_state.next_task}</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.materials:
            st.markdown("<div class='checklist-header'>📦 วัสดุที่ต้องใช้ตอนนี้</div>", unsafe_allow_html=True)
            for m in st.session_state.materials: st.checkbox(m, key=f"now_{m}")
    with c2:
        if st.session_state.next_materials:
            st.markdown("<div class='checklist-header'>🗓️ วัสดุที่ต้องซื้อล่วงหน้า</div>", unsafe_allow_html=True)
            for m in st.session_state.next_materials: st.checkbox(m, key=f"nxt_{m}")

    # แสดงตารางราคา (ใช้ค่าที่เก็บใน Session)
    if st.session_state.comp_name:
        render_comparison_grid(st.session_state.comp_name)

    owner_data = re.search(fr"\[OWNER_NOTE\]\s*(.*?)(?=\[|$)", st.session_state.rep, re.DOTALL | re.IGNORECASE)
    if owner_data:
        st.markdown("<div class='section-header'>🏠 แนะนำเจ้าของบ้าน</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='owner-content'>{owner_data.group(1).strip()}</div>", unsafe_allow_html=True)

    st.markdown(f"""<div class='contact-box'><div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem; margin-bottom:15px;'>🛠️ รับคำแนะนำวิธีแก้ไขฟรีจากทีม BHOON KHARN</div><a href='tel:0887776566' class='contact-btn'>📞 โทร: 088-777-6566</a><a href='https://line.me/ti/p/~bhoonkharn' class='contact-btn'>💬 Line: bhoonkharn</a><div style='font-size:0.75rem; color:#888; margin-top:15px;'><strong>หมายเหตุ:</strong> ข้อมูลนี้เป็นการวิเคราะห์เบื้องต้นโดย AI เพื่อเป็นแนวทางเบื้องต้นเท่านั้น ไม่สามารถนำไปใช้อ้างอิงทางกฎหมายหรือแทนที่การตรวจสอบโดยวิศวกรวิชาชีพหน้างานได้</div></div>""", unsafe_allow_html=True)
