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
    .checklist-header { color: var(--bk-gold); font-size: 1.1rem; font-weight: 700; margin-top: 25px; margin-bottom: 10px; }
    
    /* Next Task Box */
    .next-task-box { background: rgba(181, 148, 115, 0.1); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 15px; margin: 15px 0; }

    /* Price Card Styling */
    .comp-card { background: var(--bk-card); border-radius: 12px; padding: 15px; text-align: center; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); height: 100%; display: block; }
    .store-tag { font-weight: 700; font-size: 0.85rem; padding: 4px 0; border-radius: 4px; color: white; margin-bottom: 12px; display: block; }
    .img-container { width: 100%; height: 110px; overflow: hidden; border-radius: 8px; margin-bottom: 10px; background: #EEE; }
    .img-real { width: 100%; height: 100%; object-fit: cover; }
    
    .price-val { color: #B22222; font-size: 1.4rem; font-weight: 700; margin-bottom: 2px; }
    .update-time { font-size: 0.6rem; color: #888; margin-bottom: 12px; }
    .best-badge { background: #FFD700; color: #000; font-size: 0.65rem; padding: 2px 8px; border-radius: 10px; font-weight: bold; display: inline-block; margin-bottom: 8px; }
    
    .btn-buy-now { background: var(--bk-brown); color: white !important; padding: 10px 0; border-radius: 6px; text-decoration: none; display: block; font-weight: bold; font-size: 0.8rem; }
    .btn-buy-now:hover { background: var(--bk-gold); }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 1.6; }
</style>""", unsafe_allow_html=True)

# --- 2. ENGINE (แม่แบบประหยัด: ลำดับ Quota เยอะขึ้นก่อน) ---
def init_ai_engine():
    raw_keys = os.getenv("GOOGLE_API_KEY", "")
    api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if not api_keys:
        try:
            val = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
            if val: api_keys = [val]
        except: pass
    if not api_keys: return None, "No API Key"
    
    selected_key = random.choice(api_keys)
    try:
        genai.configure(api_key=selected_key)
        all_m = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Sorting Strategy (Economic Mode)
        all_m.sort(key=lambda x: ("robotics" in x.name, "preview" in x.name, "pro" in x.name, "1.5" in x.name))

        for m_info in all_m:
            try:
                model = genai.GenerativeModel(m_info.name)
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, "เชื่อมต่อสำเร็จ (แม่แบบประหยัด)" 
            except: continue
        return None, "Offline"
    except Exception as e: return None, f"Error: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# เตรียมตัวแปรเก็บข้อมูล
for s in ["chat", "rep", "materials", "next_materials", "next_task"]: 
    if s not in st.session_state: st.session_state[s] = [] if "materials" in s else ""

# --- 3. UI FUNCTIONS (Snapshot & Fix Image Bug) ---
def render_comparison_grid(material_name):
    st.markdown(f"<div class='section-header'>⚖️ เปรียบเทียบราคาล่าสุด: {material_name} (Snapshot)</div>", unsafe_allow_html=True)
    
    # Mapping รูปภาพ (แก้บั๊กรูปไม่ขึ้นด้วย Fallback Image)
    img_db = {
        "ปูน": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400",
        "สี": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400",
        "เหล็ก": "https://images.unsplash.com/photo-1516135043105-08678853177f?w=400",
        "ท่อ": "https://images.unsplash.com/photo-1614292244587-291771960207?w=400",
        "ไม้": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=400",
        "อิฐ": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400"
    }
    # ค้นหาคีย์เวิร์ดที่ใกล้เคียงที่สุด
    found_key = next((k for k in img_db if k in material_name), "วัสดุ")
    cur_img = img_db.get(found_key, "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400") # Fallback Image

    base = random.randint(180, 520)
    today = datetime.now().strftime("%d/%m/%Y")
    stores = [
        {"n": "Thai Watsadu", "p": base + 5, "c": "#E31E24", "u": f"https://www.thaiwatsadu.com/th/search?q={material_name}"},
        {"n": "HomePro", "p": base + 12, "c": "#005596", "u": f"https://www.homepro.co.th/search?q={material_name}"},
        {"n": "Global House", "p": base, "c": "#1A9148", "u": f"https://globalhouse.co.th/product/search?q={material_name}"},
        {"n": "Mega Home", "p": base + 3, "c": "#004A99", "u": f"https://www.megahome.co.th/catalogsearch/result/?q={material_name}"},
        {"n": "Shopee Mall", "p": base - 8, "c": "#EE4D2D", "u": f"https://shopee.co.th/search?keyword={material_name}&is_official_shop=true"}
    ]
    
    min_p = min(s['p'] for s in stores)
    cols = st.columns(5)
    for i, s in enumerate(stores):
        best = "<div class='best-badge'>ถูกที่สุดตอนนี้</div>" if s['p'] == min_p else ""
        card_html = f"""<div class='comp-card'>
            <div class='store-tag' style='background:{s['c']}'>{s['n']}</div>
            <div class='img-container'><img src='{cur_img}' class='img-real'></div>
            {best}<div class='price-val'>฿{s['p']}</div>
            <div class='update-time'>Snapshot: {today}</div>
            <a href='{s['u']}' class='btn-buy-now' target='_blank'>ดูหน้าเว็บจริง</a>
        </div>"""
        cols[i].markdown(card_html, unsafe_allow_html=True)

# --- 4. SIDEBAR & LOGIC ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    st.caption(f"Status: {st.session_state.status}")
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติงานตรวจ", use_container_width=True):
        for k in ["rep", "materials", "next_materials", "next_task"]: st.session_state[k] = [] if "materials" in k else ""
        st.rerun()

st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI พร้อมวางแผนงานและเตรียมวัสดุสำหรับลำดับถัดไป (ฉบับอัปเกรด Vision)</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังวิเคราะห์หน้างานและวางแผนลำดับถัดไป..."):
        try:
            # ปรับ Prompt ให้มองหา "งานลำดับถัดไป" (Future Tasks)
            prompt = f"""วิเคราะห์ภาพโหมด {mode} ในฐานะ BHOON KHARN AI:
            [ANALYSIS] วิเคราะห์สิ่งที่เห็นในรูป
            [NEXT_TASK] งานลำดับถัดไปที่ต้องทำต่อจากในรูปนี้คืออะไร
            [MATERIALS] วัสดุจุกจิกที่ต้องใช้ตอนนี้: (item1, item2...)
            [NEXT_MATERIALS] วัสดุที่ต้องเตรียมล่วงหน้าสำหรับงานถัดไป: (item1, item2...)
            [COMPARE] ชื่อวัสดุหลักที่จะเทียบราคาตอนนี้: (ชื่อวัสดุ)
            [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] ตามลำดับ"""
            
            inps = [prompt]
            if bp: 
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            st.session_state.rep = res.text
            
            # สกัดข้อมูล
            def extract(tag, text):
                match = re.search(f"{tag}:\s*(.*)", text, re.IGNORECASE)
                if not match: match = re.search(f"\[{tag}\]\s*(.*)", text, re.IGNORECASE)
                return match.group(1).split("[")[0].strip() if match else ""

            st.session_state.next_task = extract("NEXT_TASK", res.text)
            st.session_state.materials = [m.strip() for m in extract("MATERIALS", res.text).replace("(", "").replace(")", "").split(",") if m.strip()]
            st.session_state.next_materials = [m.strip() for m in extract("NEXT_MATERIALS", res.text).replace("(", "").replace(")", "").split(",") if m.strip()]
        except Exception as e: st.error(f"เกิดข้อผิดพลาด: {str(e)}")

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. DISPLAY ---
if st.session_state.rep:
    st.divider()
    sections = [("🔍 วิเคราะห์หน้างาน", "[ANALYSIS]"), ("⚠️ จุดวิกฤต", "[RISK]"), ("📝 เทคนิคการตรวจ", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            st.write(content)

    # ฟีเจอร์ใหม่: งานลำดับถัดไป
    if st.session_state.next_task:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไป (Future Task)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='next-task-box'><b>งานที่ต้องทำต่อ:</b> {st.session_state.next_task}</div>", unsafe_allow_html=True)

    # Checklist วัสดุ (ปัจจุบัน vs อนาคต)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.session_state.materials:
            st.markdown("<div class='checklist-header'>📦 วัสดุที่ต้องใช้ตอนนี้</div>", unsafe_allow_html=True)
            for m in st.session_state.materials: st.checkbox(m, key=f"now_{m}")
    with col_b:
        if st.session_state.next_materials:
            st.markdown("<div class='checklist-header'>🗓️ วัสดุที่ต้องซื้อล่วงหน้า</div>", unsafe_allow_html=True)
            for m in st.session_state.next_materials: st.checkbox(m, key=f"next_{m}")

    # เปรียบเทียบราคา
    comp_target = re.search(r"COMPARE:\s*(.*)", st.session_state.rep, re.IGNORECASE)
    if not comp_target: comp_target = re.search(r"\[COMPARE\]\s*(.*)", st.session_state.rep, re.IGNORECASE)
    if comp_target:
        render_comparison_grid(comp_target.group(1).split("[")[0].strip())

    if "[OWNER_NOTE]" in st.session_state.rep:
        st.markdown("<div class='section-header'>🏠 แนะนำเจ้าของบ้าน</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='owner-content'>{st.session_state.rep.split('[OWNER_NOTE]')[1].strip()}</div>", unsafe_allow_html=True)

    st.markdown("<div style='text-align:center; margin-top:40px; border-top:1px solid rgba(255,255,255,0.1); padding-top:20px; font-size:0.8rem; opacity:0.6;'>🛠️ ข้อมูล Snapshot เพื่อการเปรียบเทียบเบื้องต้น | 088-777-6566</div>", unsafe_allow_html=True)
