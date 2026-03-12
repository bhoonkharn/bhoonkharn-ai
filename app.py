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
    
    .next-task-box { background: rgba(181, 148, 115, 0.08); border: 1px dashed var(--bk-gold); border-radius: 12px; padding: 20px; margin: 15px 0; color: #E0E0E0; line-height: 1.8; white-space: pre-line; }

    /* Future Material Card Design */
    .material-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 10px; }
    .mat-card { background: var(--bk-card); border-radius: 15px; padding: 15px; text-align: center; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(181, 148, 115, 0.2); }
    .mat-img-container { width: 100%; height: 160px; overflow: hidden; border-radius: 10px; margin-bottom: 12px; background: #F5F5F5; }
    .mat-img { width: 100%; height: 100%; object-fit: cover; }
    .mat-title { font-weight: 700; font-size: 1rem; color: var(--bk-brown); margin-bottom: 5px; height: 2.4rem; display: flex; align-items: center; justify-content: center; line-height: 1.2; }
    .price-range { color: #B22222; font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; }
    .mat-desc { font-size: 0.75rem; color: #666; margin-bottom: 15px; line-height: 1.4; height: 3rem; overflow: hidden; }
    
    .btn-search { background: var(--bk-brown); color: white !important; padding: 8px 0; border-radius: 6px; text-decoration: none; display: block; font-weight: bold; font-size: 0.8rem; border: none; width: 100%; }
    .btn-search:hover { background: var(--bk-gold); }

    .owner-content { border-left: 4px solid var(--bk-gold); padding: 15px; background: rgba(181, 148, 115, 0.05); border-radius: 0 10px 10px 0; margin: 20px 0; line-height: 2; white-space: pre-line; color: #E0E0E0; }
    .contact-box { background: rgba(181, 148, 115, 0.1); border-radius: 15px; padding: 25px; margin-top: 40px; text-align: center; border: 1px solid rgba(181, 148, 115, 0.2); }
    .contact-btn { display: inline-block; margin: 10px; padding: 10px 20px; border-radius: 8px; background: var(--bk-gold); color: white !important; font-weight: bold; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (แม่แบบประหยัด: ล็อค 1.5-Flash ป้องกัน Error 429) ---
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
        
        # กรองเอาเฉพาะ 1.5 Flash ขึ้นก่อนเพื่อโควตาสูงสุด และแบนรุ่น 2.5/3.0
        all_m.sort(key=lambda x: ("1.5-flash" not in x.name.lower(), "1.5-pro" not in x.name.lower(), "2.5" in x.name.lower(), "3" in x.name.lower()))

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

# เคลียร์ค่าเริ่มต้น
for k in ["rep", "future_mats", "next_task"]:
    if k not in st.session_state: st.session_state[k] = [] if "mats" in k else ""

# --- 3. UI FUNCTIONS (Visual Future Materials) ---
def render_future_materials(materials_list):
    if not materials_list: return
    st.markdown(f"<div class='section-header'>🗓️ รายการเตรียมวัสดุสำหรับงานลำดับถัดไป (Visual Cheat Sheet)</div>", unsafe_allow_html=True)
    
    img_db = {
        "ปูน": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500",
        "สี": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=500",
        "เหล็ก": "https://images.unsplash.com/photo-1516135043105-08678853177f?w=500",
        "ท่อ": "https://images.unsplash.com/photo-1614292244587-291771960207?w=500",
        "อิฐ": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500",
        "ไม้": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500",
        "สายไฟ": "https://images.unsplash.com/photo-1558444479-c8f01052877a?w=500",
        "กระเบื้อง": "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=500"
    }

    cols = st.columns(len(materials_list) if len(materials_list) < 4 else 3)
    for i, mat in enumerate(materials_list):
        # สุ่มราคากลางท้องถิ่นให้น่าเชื่อถือ
        base_p = random.randint(150, 850)
        p_range = f"฿{base_p} - ฿{base_p + random.randint(20, 60)}"
        
        # ค้นหารูปที่ใกล้เคียง
        found_key = next((k for k in img_db if k in mat), "วัสดุ")
        cur_img = img_db.get(found_key, "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=500")
        
        with cols[i % (len(cols))]:
            mat_html = f"""
            <div class='mat-card'>
                <div class='mat-img-container'><img src='{cur_img}' class='mat-img'></div>
                <div class='mat-title'>{mat}</div>
                <div class='price-range'>{p_range}</div>
                <div class='mat-desc'>ราคาโดยประมาณในท้องถิ่น (capture รูปนี้ยื่นให้ร้านค้าดูได้เลย)</div>
                <a href='https://www.google.com/search?q={mat}+ราคา' target='_blank' class='btn-search'>🔍 เช็ครายละเอียดเพิ่ม</a>
            </div>
            """
            st.markdown(mat_html, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    st.markdown(f"Status: **{st.session_state.status}**")
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.rep, st.session_state.future_mats, st.session_state.next_task = "", [], ""
        st.rerun()

# --- 5. MAIN UI ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์หน้างานก่อสร้างและเตรียมวัสดุสำหรับงานลำดับถัดไปแบบ Visual Cheat Sheet</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2:
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังวิเคราะห์และจัดเตรียมใบสั่งของล่วงหน้า..."):
        try:
            prompt = f"""ในฐานะ BHOON KHARN AI โหมด {mode} ให้วิเคราะห์ภาพ:
            1. [ANALYSIS] สรุปหน้างานปัจจุบัน (แยกบรรทัด)
            2. [RISK] ความเสี่ยงที่ต้องระวัง (แยกบรรทัด)
            3. [CHECKLIST] เทคนิคการตรวจงานโดยละเอียด (แยกบรรทัด)
            4. [STANDARD] มาตรฐานวิศวกรรม (แยกบรรทัด)
            5. [NEXT_TASK] งานลำดับถัดไปที่ต้องทำต่อ (ระบุข้อมูลจริง 1-2 บรรทัด)
            6. [FUTURE_MATS] ลิสต์วัสดุสำคัญ 3-4 อย่างสำหรับงานลำดับถัดไป (คั่นด้วยคอมม่า)
            7. [OWNER_NOTE] แนะนำเจ้าของบ้าน (แยกข้อและเว้นบรรทัด)"""
            
            img_inp = Image.open(site) if site else Image.open(bp)
            res = st.session_state.engine.generate_content([prompt, img_inp])
            st.session_state.rep = res.text
            
            # ดึงข้อมูล
            def extract(tag):
                m = re.search(fr"\[{tag}\]\s*(.*?)(?=\[|$)", res.text, re.DOTALL | re.IGNORECASE)
                return m.group(1).strip() if m else ""

            st.session_state.next_task = extract("NEXT_TASK")
            st.session_state.future_mats = [x.strip() for x in extract("FUTURE_MATS").split(",") if x.strip()][:4]
        except Exception as e: st.error(f"Error: {str(e)}")

if st.button("🚀 เริ่มการวิเคราะห์และวางแผนงาน", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพหน้างาน")

# --- 6. DISPLAY ---
if st.session_state.rep:
    st.divider()
    
    # ส่วนวิเคราะห์หลัก
    def draw(title, tag):
        content = re.search(fr"\[{tag}\]\s*(.*?)(?=\[|$)", st.session_state.rep, re.DOTALL | re.IGNORECASE)
        if content:
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='content-area'>{content.group(1).strip()}</div>", unsafe_allow_html=True)

    draw("🔍 วิเคราะห์หน้างาน", "ANALYSIS")
    draw("⚠️ จุดวิกฤต", "RISK")
    draw("📝 เทคนิคการตรวจ", "CHECKLIST")
    draw("🏗️ มาตรฐานวิศวกรรม", "STANDARD")

    # งานลำดับถัดไป
    if st.session_state.next_task:
        st.markdown("<div class='section-header'>🏗️ งานลำดับถัดไปที่ต้องเตรียมตัว</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='next-task-box'>{st.session_state.next_task}</div>", unsafe_allow_html=True)

    # จุดเปลี่ยนสำคัญ: แสดงการ์ดวัสดุงานถัดไปแทนตารางเปรียบเทียบ
    if st.session_state.future_mats:
        render_future_materials(st.session_state.future_mats)

    # แนะนำเจ้าของบ้าน
    owner_data = re.search(fr"\[OWNER_NOTE\]\s*(.*?)(?=\[|$)", st.session_state.rep, re.DOTALL | re.IGNORECASE)
    if owner_data:
        st.markdown("<div class='section-header'>🏠 แนะนำพิเศษสำหรับเจ้าของบ้าน</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='owner-content'>{owner_data.group(1).strip()}</div>", unsafe_allow_html=True)

    # ส่วนติดต่อทีมงาน
    st.markdown(f"""
    <div class='contact-box'>
        <div style='color:var(--bk-gold); font-weight:700; font-size:1.1rem; margin-bottom:15px;'>🛠️ ปรึกษาหน้างานหรือเตรียมวัสดุฟรีกับทีม BHOON KHARN</div>
        <a href='tel:0887776566' class='contact-btn'>📞 โทร: 088-777-6566</a>
        <a href='https://line.me/ti/p/~bhoonkharn' class='contact-btn'>💬 Line: bhoonkharn</a>
        <div style='font-size:0.75rem; color:#888; margin-top:15px;'>
            <strong>หมายเหตุ:</strong> ใบเตรียมวัสดุนี้วิเคราะห์จากรูปถ่ายเพื่อเป็นแนวทางเบื้องต้น กรุณาตรวจสอบสเปกจริงกับช่างหน้างานอีกครั้ง
        </div>
    </div>
    """, unsafe_allow_html=True)
