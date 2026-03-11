import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import os        # ดึงค่าจาก Google Cloud
import random    # สลับ 7 คีย์

# --- 1. CONFIG & STYLE (Premium Dark Brown & Gold) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; --bk-card: #FFFFFF; }
    
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-bottom: 0px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; padding: 0 10%; }
    
    /* Checklist Table Styling */
    .checklist-header { color: var(--bk-gold); font-size: 1.1rem; font-weight: 700; margin-top: 30px; margin-bottom: 10px; }
    .stCheckbox label { color: #E0E0E0 !important; font-size: 0.9rem; }
    
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 8px; margin-top: 30px; }
    
    /* Price Comparison Card (Same Brand Focus) */
    .comp-card { background: var(--bk-card); border-radius: 12px; padding: 15px; text-align: center; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.3); height: 100%; }
    .store-tag { font-weight: 700; font-size: 0.9rem; margin-bottom: 8px; }
    .price-val { color: #B22222; font-size: 1.4rem; font-weight: 700; margin: 10px 0; }
    .best-price { background: #FFD700; color: #000; font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: bold; }
    .img-box { border: 1px dashed #DDD; height: 100px; display: flex; align-items: center; justify-content: center; background: #F9F9F9; margin-bottom: 10px; border-radius: 8px; color: #999; font-size: 0.7rem; }
    
    .btn-buy { background: var(--bk-brown); color: white !important; padding: 8px 0; border-radius: 6px; text-decoration: none; display: block; font-weight: bold; font-size: 0.8rem; }
    .btn-buy:hover { background: var(--bk-gold); }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 1.6; }
    .maroon-note { color: #FF6B6B; font-size: 0.8rem; text-align: center; margin-top: 40px; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (แม่แบบเดิม 100% - ซ่อนชื่อโมเดลตามสั่ง) ---
def init_ai_engine():
    raw_keys = os.getenv("GOOGLE_API_KEY", "")
    api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if not api_keys:
        try:
            val = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
            if val: api_keys = [val]
        except: pass
    if not api_keys: return None, "กรุณาตั้งค่า API Key"
    
    selected_key = random.choice(api_keys)
    try:
        genai.configure(api_key=selected_key)
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models.sort(key=lambda x: ("pro" in x.name, "1.5" in x.name), reverse=True)
        for m_info in models:
            try:
                model = genai.GenerativeModel(m_info.name)
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, "เชื่อมต่อสำเร็จ" # ซ่อนชื่อรุ่น AI
            except: continue
        return None, "Offline"
    except Exception as e: return None, f"Error: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

for s in ["chat", "rep", "qs", "materials"]: 
    if s not in st.session_state: st.session_state[s] = [] if s != "rep" else ""

# --- 3. UI FUNCTIONS (Checklist & Comparison) ---
def render_shopping_checklist(mat_list):
    st.markdown("<div class='checklist-header'>📋 รายการวัสดุที่ต้องใช้ (Shopping Checklist)</div>", unsafe_allow_html=True)
    for item in mat_list:
        st.checkbox(f"{item.strip()}", key=f"check_{item}")

def render_comparison_grid(material_name):
    st.markdown(f"<div class='section-header'>⚖️ เปรียบเทียบราคา: {material_name} (ยี่ห้อเดียวกัน)</div>", unsafe_allow_html=True)
    
    # ข้อมูลจำลองราคาแบบ Apples to Apples
    stores = [
        {"name": "Thai Watsadu", "price": 185, "link": "#", "color": "#E31E24"},
        {"name": "HomePro", "price": 195, "link": "#", "color": "#005596"},
        {"name": "Global House", "price": 182, "link": "#", "color": "#1A9148"},
        {"name": "Mega Home", "price": 189, "link": "#", "color": "#004A99"},
        {"name": "Shopee Mall", "price": 179, "link": "#", "color": "#EE4D2D"}
    ]
    # หาราคาที่ถูกที่สุด
    min_price = min(s['price'] for s in stores)
    
    cols = st.columns(len(stores))
    for i, store in enumerate(stores):
        with cols[i]:
            is_best = " <span class='best-price'>ถูกที่สุด</span>" if store['price'] == min_price else ""
            st.markdown(f"""
            <div class='comp-card'>
                <div class='store-tag' style='color:{store['color']}'>{store['name']}</div>
                <div class='img-box'>[ รูป {material_name} ]</div>
                <div class='price-val'>฿{store['price']}{is_best}</div>
                <a href='{store['link']}' class='btn-buy' target='_blank'>ไปที่ร้านค้า</a>
            </div>
            """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    if "สำเร็จ" in st.session_state.status: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.materials = [], "", []; st.rerun()

# --- 5. MAIN UI ---
st.markdown("<h1 class='main-title'>BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม คัดสรรวัสดุมาตรฐานสูงสุดจาก 5 ร้านค้าชั้นนำเพื่อความคุ้มค่าและปลอดภัย</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 6. LOGIC (แม่แบบเดิม 100%) ---
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("กำลังวิเคราะห์วัสดุและสเปกทางวิศวกรรม..."):
        try:
            prompt = f"วิเคราะห์ภาพโหมด {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และสรุปรายการวัสดุที่เกี่ยวข้องทั้งหมดใน Tag [MATERIALS: item1, item2...] และระบุชื่อวัสดุหลักที่จะเทียบราคาใน [COMPARE:ชื่อวัสดุ]"
            inps = [prompt]
            if bp: 
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            st.session_state.rep = res.text
            
            # สกัดรายการวัสดุสำหรับ Checklist
            mats = re.search(r"\[MATERIALS:(.*)\]", res.text)
            if mats: st.session_state.materials = [m.strip() for m in mats.group(1).split(",")]
        except Exception as e: st.error(str(e))

# --- 7. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

if st.session_state.rep:
    st.divider()
    sections = [("🔍 สรุปการวิเคราะห์", "[ANALYSIS]"), ("⚠️ จุดวิกฤต", "[RISK]"), ("📝 เทคนิคการตรวจ", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 คำแนะนำเจ้าของบ้าน", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # แสดง Shopping Checklist (ส่วนที่เพิ่มใหม่)
    if st.session_state.materials:
        render_shopping_checklist(st.session_state.materials)
    
    # แสดงตารางเปรียบเทียบราคา (ส่วนที่เพิ่มใหม่)
    comp_match = re.search(r"\[COMPARE:(.*)\]", st.session_state.rep)
    if comp_match:
        render_comparison_grid(comp_match.group(1).strip())

    st.markdown("<div class='maroon-note'>หมายเหตุ: ข้อมูล AI เบื้องต้น ไม่สามารถใช้อ้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
