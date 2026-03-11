import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import os        # ดึงค่าจาก Google Cloud
import random    # สลับคีย์

# --- 1. CONFIG & STYLE (ปรับเป็นโทนสีน้ำตาล-ทอง Premium) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-brown: #4A3F35; --bk-light: #FDFBF9; }
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.8; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; margin-bottom: 5px; font-size: 2.2rem; }
    .story-text { text-align: center; color: var(--bk-brown); font-size: 0.9rem; margin-bottom: 30px; opacity: 0.8; padding: 0 10%; }
    .section-header { color: var(--bk-gold); font-size: 1.2rem; font-weight: 700; margin-top: 25px; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .owner-content { border-left: 5px solid var(--bk-gold); padding-left: 20px; margin: 20px 0; background: transparent !important; color: inherit !important; font-size: 1rem; white-space: pre-line; }
    div.stButton > button { font-size: 0.75rem !important; border-radius: 10px !important; color: var(--bk-brown) !important; border: 1px solid var(--bk-gold) !important; }
    div.stButton > button:hover { background-color: var(--bk-gold) !important; color: white !important; }
    
    /* สไตล์กล่องเปรียบเทียบราคาแบบใหม่ (Card View) */
    .comp-card { background: white; border: 1px solid #eee; border-radius: 12px; padding: 15px; text-align: center; transition: 0.3s; }
    .comp-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-color: var(--bk-gold); }
    .store-logo { font-weight: bold; font-size: 1rem; margin-bottom: 10px; display: block; color: var(--bk-brown); }
    .price-tag { color: #B22222; font-size: 1.2rem; font-weight: 700; margin: 10px 0; }
    .item-img { width: 100%; border-radius: 8px; margin-bottom: 10px; background: #f9f9f9; height: 120px; display: flex; align-items: center; justify-content: center; color: #ccc; font-size: 0.8rem; border: 1px dashed #ddd; }
    .aff-btn { display: block; text-align: center; padding: 8px; font-size: 0.8rem; border-radius: 6px; text-decoration: none; background: var(--bk-brown); color: white !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (แม่แบบเดิม 100% - ปรับแค่การซ่อนชื่อรุ่น AI) ---
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
        # ขั้นตอนสแกนหาตัวใหม่ล่าสุดตามแม่แบบเดิม
        available_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        available_models.sort(key=lambda x: ("pro" in x.name, "1.5" in x.name), reverse=True)

        for m_info in available_models:
            try:
                model = genai.GenerativeModel(m_info.name)
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                # ปรับแก้: ไม่โชว์ชื่อ model ในสถานะตามคำสั่งข้อ 2
                return model, "เชื่อมต่อสำเร็จ" 
            except: continue
        return None, "ไม่พบโมเดลที่พร้อมใช้งาน"
    except Exception as e:
        return None, f"การเชื่อมต่อขัดข้อง: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. ฟังก์ชันเปรียบเทียบราคาแบบใหม่ (โชว์รูปและราคาตามคำสั่งข้อ 3) ---
def render_comparison_suite(material_name):
    st.markdown(f"<div class='section-header'>📊 เปรียบเทียบราคาวัสดุทางการ: {material_name}</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # ข้อมูลจำลอง (ในอนาคตจะดึงจาก API Affiliate)
    stores = [
        {"name": "Shopee Mall", "price": "฿XXX - ฿,XXX", "color": "#EE4D2D", "link": f"https://shopee.co.th/search?keyword={material_name}&is_official_shop=true"},
        {"name": "Thai Watsadu", "price": "฿XXX - ฿,XXX", "color": "#E31E24", "link": f"https://www.thaiwatsadu.com/th/search?q={material_name}"},
        {"name": "HomePro", "price": "฿XXX - ฿,XXX", "color": "#005596", "link": f"https://www.homepro.co.th/search?q={material_name}"}
    ]
    
    cols = [col1, col2, col3]
    for i, store in enumerate(stores):
        with cols[i]:
            st.markdown(f"""
            <div class='comp-card'>
                <span class='store-logo' style='color:{store['color']}'>{store['name']}</span>
                <div class='item-img'>[ รูปภาพสินค้า {material_name} ]</div>
                <div class='price-tag'>{store['price']}</div>
                <a href='{store['link']}' class='aff-btn' target='_blank'>ดูรายละเอียด</a>
            </div>
            """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    if "สำเร็จ" in st.session_state.status: st.success(st.session_state.status)
    else: st.error(st.session_state.status)
    if st.button("🔄 เริ่มต้นระบบใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("มุมมองการแสดงผล:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติงานตรวจ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# --- 5. MAIN UI ---
st.markdown("<h1 class='main-title'>BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม คัดสรรวัสดุมาตรฐานจากร้านค้าทางการเพื่อความมั่นใจสูงสุด</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนก่อสร้าง", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 สภาพหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 6. LOGIC (แม่แบบเดิม 100%) ---
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            # ใช้ Prompt เดิมที่คุณวางไว้เป๊ะๆ แต่เพิ่มคำสั่งสกัดชื่อวัสดุเล็กน้อย
            prompt = f"วิเคราะห์ฐานะ BHOON KHARN AI โหมด: {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และระบุชื่อวัสดุหลัก 1 อย่างในรูปแบบ [MATERIAL:ชื่อวัสดุ] แนะนำ 3 คำถาม 'ถามช่าง: '"
            inps = [prompt]
            if bp:
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            txt = res.text
            st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.rep = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            st.session_state.chat = []
        except Exception as e: st.error(f"เกิดข้อผิดพลาด: {str(e)}")

# --- 7. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

if st.session_state.rep:
    st.divider()
    sections = [("🔍 สรุปการวิเคราะห์", "[ANALYSIS]"), ("⏱️ จุดวิกฤต", "[RISK]"), ("📝 เทคนิคการตรวจ", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 คำแนะนำเจ้าของบ้าน", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # ดึงชื่อวัสดุมาแสดงตารางเปรียบเทียบราคา (ส่วนที่เพิ่มใหม่)
    mat_match = re.search(r"\[MATERIAL:(.*)\]", st.session_state.rep)
    if mat_match:
        render_comparison_suite(mat_match.group(1).strip())

    st.markdown("<div class='maroon-note'><strong>หมายเหตุ:</strong> ข้อมูล AI เบื้องต้น ไม่สามารถใช้อ้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
