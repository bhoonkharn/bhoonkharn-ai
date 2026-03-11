import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import os        # ดึงค่าจาก Google Cloud
import random    # สลับ 7 คีย์

# --- 1. CONFIG & STYLE (แม่แบบเดิม - โทนน้ำตาลทองพรีเมียม) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-dark: #1E1A17; --bk-card: #FFFFFF; }
    
    html, body, [class*="st-app"] { background-color: var(--bk-dark); color: #F5F5F5; font-family: 'Sarabun', sans-serif; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 2.2rem; margin-bottom: 0px; }
    .story-text { text-align: center; color: #A09080; font-size: 0.85rem; margin-bottom: 30px; padding: 0 10%; }
    
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(181, 148, 115, 0.3); padding-bottom: 8px; margin-top: 30px; }
    
    /* Checklist Table */
    .checklist-header { color: var(--bk-gold); font-size: 1.1rem; font-weight: 700; margin-top: 30px; margin-bottom: 10px; }
    
    /* Price Comparison Card (ปรับปรุงให้ดูเหมือนหน้าขายจริง) */
    .comp-card { background: var(--bk-card); border-radius: 12px; padding: 15px; text-align: center; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.3); height: 100%; transition: 0.3s; }
    .comp-card:hover { transform: translateY(-5px); }
    .store-tag { font-weight: 700; font-size: 0.9rem; margin-bottom: 8px; border-radius: 4px; padding: 2px 0; color: white; }
    
    .img-box-real { width: 100%; height: 130px; object-fit: contain; margin-bottom: 10px; border-radius: 8px; background: #FFF; }
    .price-status { color: #B22222; font-size: 1.1rem; font-weight: 700; margin: 10px 0; }
    .best-label { background: #FFD700; color: #000; font-size: 0.65rem; padding: 2px 8px; border-radius: 10px; font-weight: bold; display: inline-block; margin-bottom: 5px; }
    
    .btn-buy-now { background: var(--bk-brown); color: white !important; padding: 10px 0; border-radius: 6px; text-decoration: none; display: block; font-weight: bold; font-size: 0.85rem; }
    .btn-buy-now:hover { background: var(--bk-gold); }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 1.6; }
    .maroon-note { color: #FF6B6B; font-size: 0.8rem; text-align: center; margin-top: 40px; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ล็อคแม่แบบเดิม 100% ห้ามแก้) ---
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

# --- 3. UI FUNCTIONS (ปรับปรุงให้โชว์รูปจริงและลิ้งค์ซื้อจริง) ---
def render_comparison_grid(material_name):
    st.markdown(f"<div class='section-header'>⚖️ เช็คราคาและสั่งซื้อ: {material_name} (ยี่ห้อเดียวกัน)</div>", unsafe_allow_html=True)
    
    # ดึงรูปตัวแทนตามหมวดหมู่ (ใช้รูปจริงจาก Unsplash หรือ Placeholder คุณภาพสูง)
    img_url = "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=300&auto=format&fit=crop" # รูปปูน/วัสดุก่อสร้าง
    if "สี" in material_name: img_url = "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?q=80&w=300&auto=format&fit=crop"
    elif "เหล็ก" in material_name: img_url = "https://images.unsplash.com/photo-1516135043105-08678853177f?q=80&w=300&auto=format&fit=crop"

    # ระบบลิ้งค์ค้นหาจริง (Search Link Construction)
    stores = [
        {"name": "Thai Watsadu", "color": "#E31E24", "link": f"https://www.thaiwatsadu.com/th/search?q={material_name}"},
        {"name": "HomePro", "color": "#005596", "link": f"https://www.homepro.co.th/search?q={material_name}"},
        {"name": "Global House", "color": "#1A9148", "link": f"https://globalhouse.co.th/product/search?q={material_name}"},
        {"name": "Mega Home", "color": "#004A99", "link": f"https://www.megahome.co.th/catalogsearch/result/?q={material_name}"},
        {"name": "Shopee Mall", "color": "#EE4D2D", "link": f"https://shopee.co.th/search?keyword={material_name}&is_official_shop=true"}
    ]
    
    cols = st.columns(len(stores))
    for i, store in enumerate(stores):
        with cols[i]:
            st.markdown(f"""
            <div class='comp-card'>
                <div class='store-tag' style='background:{store['color']}'>{store['name']}</div>
                <img src='{img_url}' class='img-box-real'>
                <div class='best-label'>คลิกดูราคาโปรโมชั่น</div>
                <div class='price-status'>เช็คราคาสด</div>
                <a href='{store['link']}' class='btn-buy-now' target='_blank'>สั่งซื้อเลย</a>
            </div>
            """, unsafe_allow_html=True)

# --- 4. SIDEBAR & MAIN UI (แม่แบบเดิม) ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    if "สำเร็จ" in st.session_state.status: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.materials = [], "", []; st.rerun()

st.markdown("<h1 class='main-title'>BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม พร้อมระบบเช็คราคาและสั่งซื้อวัสดุจาก 5 ห้างชั้นนำโดยตรง</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 5. LOGIC & DISPLAY (แม่แบบเดิม 100%) ---
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("กำลังตรวจสอบหน้างานและเปรียบเทียบวัสดุ..."):
        try:
            prompt = f"วิเคราะห์ภาพโหมด {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และสรุปรายการวัสดุจุกจิกทั้งหมดใน [MATERIALS: item1, item2...] และระบุชื่อวัสดุหลักที่จะเทียบราคาใน [COMPARE:ชื่อวัสดุ]"
            inps = [prompt]
            if bp: 
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            st.session_state.rep = res.text
            mats = re.search(r"\[MATERIALS:(.*)\]", res.text)
            if mats: st.session_state.materials = [m.strip() for m in mats.group(1).split(",")]
        except Exception as e: st.error(str(e))

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

if st.session_state.rep:
    st.divider()
    sections = [("🔍 ผลการวิเคราะห์", "[ANALYSIS]"), ("⚠️ จุดวิกฤต", "[RISK]"), ("📝 เทคนิคการตรวจ", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 คำแนะนำเจ้าของบ้าน", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # แสดง Shopping Checklist
    if st.session_state.materials:
        st.markdown("<div class='checklist-header'>📋 รายการวัสดุจุกจิกที่ต้องเตรียม</div>", unsafe_allow_html=True)
        for item in st.session_state.materials:
            st.checkbox(f"{item.strip()}", key=f"check_{item}")
    
    # แสดงตารางเปรียบเทียบและลิ้งค์ซื้อจริง (ส่วนที่เพิ่มใหม่)
    comp_match = re.search(r"\[COMPARE:(.*)\]", st.session_state.rep)
    if comp_match:
        render_comparison_grid(comp_match.group(1).strip())

    st.markdown("<div class='maroon-note'>หมายเหตุ: ข้อมูลราคาโปรโมชั่นเป็นไปตามเงื่อนไขของร้านค้า กรุณาตรวจสอบอีกครั้งก่อนสั่งซื้อ</div>", unsafe_allow_html=True)
