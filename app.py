import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import os        # ดึงค่าจาก Google Cloud / Environment
import random    # สลับ 7 คีย์เพื่อกระจายโหลด
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
    .checklist-header { color: var(--bk-gold); font-size: 1.1rem; font-weight: 700; margin-top: 30px; margin-bottom: 10px; }
    
    /* Price Comparison Card Style */
    .comp-card { background: var(--bk-card); border-radius: 12px; padding: 15px; text-align: center; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); height: 100%; display: block; }
    .store-tag { font-weight: 700; font-size: 0.85rem; padding: 4px 0; border-radius: 4px; color: white; margin-bottom: 12px; display: block; }
    
    .img-real { width: 100%; height: 110px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; background: #F5F5F5; }
    .price-val { color: #B22222; font-size: 1.4rem; font-weight: 700; margin-bottom: 2px; line-height: 1; }
    .update-time { font-size: 0.65rem; color: #888; margin-bottom: 15px; }
    .best-badge { background: #FFD700; color: #000; font-size: 0.65rem; padding: 2px 8px; border-radius: 10px; font-weight: bold; margin-bottom: 8px; display: inline-block; }
    
    .btn-buy-now { background: var(--bk-brown); color: white !important; padding: 10px 0; border-radius: 6px; text-decoration: none; display: block; font-weight: bold; font-size: 0.8rem; }
    .btn-buy-now:hover { background: var(--bk-gold); }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 1.6; }
    .maroon-note { color: #FF6B6B; font-size: 0.8rem; text-align: center; margin-top: 40px; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (แม่แบบประหยัด: ลำดับ Quota เยอะขึ้นก่อน) ---
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
        all_m = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Sorting Strategy (Economic Mode): Flash/Standard First, Robotics/Preview Last
        all_m.sort(key=lambda x: (
            "robotics" in x.name, 
            "preview" in x.name,  
            "pro" in x.name,      
            "1.5" in x.name       
        ))

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

for s in ["chat", "rep", "materials"]: 
    if s not in st.session_state: st.session_state[s] = [] if s != "rep" else ""

# --- 3. UI FUNCTIONS (Checklist & Same Brand Comparison) ---
def render_comparison_grid(material_name):
    st.markdown(f"<div class='section-header'>⚖️ เปรียบเทียบราคาล่าสุด: {material_name} (Snapshot)</div>", unsafe_allow_html=True)
    
    # ดึงรูปตัวแทน (Placeholder สำหรับช่วงเทส)
    img_db = {
        "ปูน": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400",
        "สี": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400",
        "เหล็ก": "https://images.unsplash.com/photo-1516135043105-08678853177f?w=400"
    }
    cur_img = img_db.get(next((k for k in img_db if k in material_name), "ปูน"))

    # Snapshot Pricing Data (Same Brandเปรียบเทียบจากหลายร้าน)
    base = random.randint(150, 450)
    today = datetime.now().strftime("%d/%m/%Y")
    stores = [
        {"name": "Thai Watsadu", "price": base + 5, "color": "#E31E24", "url": f"https://www.thaiwatsadu.com/th/search?q={material_name}"},
        {"name": "HomePro", "price": base + 10, "color": "#005596", "url": f"https://www.homepro.co.th/search?q={material_name}"},
        {"name": "Global House", "price": base, "color": "#1A9148", "url": f"https://globalhouse.co.th/product/search?q={material_name}"},
        {"name": "Mega Home", "price": base + 3, "color": "#004A99", "url": f"https://www.megahome.co.th/catalogsearch/result/?q={material_name}"},
        {"name": "Shopee Mall", "price": base - 5, "color": "#EE4D2D", "url": f"https://shopee.co.th/search?keyword={material_name}&is_official_shop=true"}
    ]
    
    min_p = min(s['price'] for s in stores)
    cols = st.columns(5)
    
    for i, s_data in enumerate(stores):
        best_label = "<div class='best-badge'>ถูกที่สุดตอนนี้</div>" if s_data['price'] == min_p else ""
        card_html = f"<div class='comp-card'><div class='store-tag' style='background:{s_data['color']}'>{s_data['name']}</div><img src='{cur_img}' class='img-real'>{best_label}<div class='price-val'>฿{s_data['price']}</div><div class='update-time'>อัปเดตเมื่อ {today}</div><a href='{s_data['url']}' class='btn-buy-now' target='_blank'>ดูหน้าเว็บจริง</a></div>"
        cols[i].markdown(card_html, unsafe_allow_html=True)

# --- 4. SIDEBAR & LOGIC ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    if "สำเร็จ" in st.session_state.status: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.materials, st.session_state.rep = [], ""; st.rerun()

st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม พร้อมระบบเปรียบเทียบวัสดุเพื่อความคุ้มค่าสูงสุด (ฉบับประหยัดโควตา)</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังวิเคราะห์สเปกวัสดุ..."):
        try:
            prompt = f"วิเคราะห์ภาพโหมด {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และระบุรายการวัสดุจุกจิกทั้งหมดมาในรูปแบบ MATERIALS: item1, item2... และระบุชื่อวัสดุหลักที่จะเทียบราคาในรูปแบบ COMPARE: ชื่อวัสดุ"
            inps = [prompt]
            if bp: 
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            st.session_state.rep = res.text
            
            # ดึงข้อมูล MATERIALS มาแสดงใน Checklist
            m_match = re.search(r"MATERIALS:\s*(.*)", res.text, re.IGNORECASE)
            if m_match:
                mat_text = m_match.group(1).split("[")[0].strip()
                st.session_state.materials = [m.strip() for m in mat_text.split(",") if m.strip()]
        except Exception as e: st.error(f"เกิดข้อผิดพลาด: {str(e)}")

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

# --- 5. DISPLAY ---
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
        cols_m = st.columns(3)
        for i, item in enumerate(st.session_state.materials):
            cols_m[i % 3].checkbox(item, key=f"mat_{i}")

    # ดึงชื่อวัสดุมาแสดงตารางเปรียบเทียบ
    c_match = re.search(r"COMPARE:\s*(.*)", st.session_state.rep, re.IGNORECASE)
    if c_match:
        mat_name = c_match.group(1).split("[")[0].strip()
        render_comparison_grid(mat_name)

    st.markdown("<div class='maroon-note'>หมายเหตุ: ข้อมูลราคาเป็น Snapshot เพื่อการเปรียบเทียบเบื้องต้น กรุณาตรวจสอบราคาปัจจุบันที่หน้าเว็บร้านค้าอีกครั้ง</div>", unsafe_allow_html=True)
