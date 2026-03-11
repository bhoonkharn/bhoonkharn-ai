import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import os        # เพิ่มเพื่อดึงค่าจาก Google Cloud
import random    # เพิ่มเพื่อสลับ 7 คีย์

# --- 1. CONFIG & STYLE (คงเดิมตามต้นฉบับของคุณ 100%) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.8; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 5px; }
    .story-text { text-align: center; color: #444; font-size: 0.9rem; margin-bottom: 30px; opacity: 0.8; padding: 0 10%; }
    .section-header { color: #1E3A8A; font-size: 1.2rem; font-weight: 700; margin-top: 25px; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .owner-content { border-left: 5px solid #1E3A8A; padding-left: 20px; margin: 20px 0; background: transparent !important; color: inherit !important; font-size: 1rem; white-space: pre-line; }
    div.stButton > button { font-size: 0.75rem !important; border-radius: 10px !important; color: #555 !important; }
    .maroon-note { color: #8B0000; font-size: 0.85rem; border-top: 1px solid #eee; margin-top: 40px; padding-top: 20px; text-align: center; }
    
    /* ส่วนเสริม: กล่องเปรียบเทียบวัสดุ (ใหม่) */
    .comp-box { border: 1px solid #ddd; border-radius: 12px; padding: 20px; margin-top: 20px; background: #fcfcfc; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .aff-btn { display: block; text-align: center; padding: 8px; margin: 5px 0; font-size: 0.8rem; border-radius: 6px; text-decoration: none; border: 1px solid #1E3A8A; color: #1E3A8A; font-weight: bold; }
    .aff-btn:hover { background: #1E3A8A; color: white; }

    .contact-box { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 15px; padding: 20px; margin-top: 30px; text-align: center; }
    .contact-title { color: #1E3A8A; font-weight: 700; font-size: 1.1rem; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ปรับปรุง: ห้ามระบุชื่อรุ่น และให้วนหาตัวที่ใหม่ที่สุดก่อนเสมอ) ---
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
        # สแกนหาโมเดลทั้งหมดที่รองรับ generateContent
        available_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # เรียงลำดับ: เลือกตัวที่ฉลาดที่สุด (Pro) และเวอร์ชั่นใหม่ (1.5) ขึ้นมาทดสอบก่อน
        # เรียงโดยใช้ Priority: Pro > 1.5 > Flash
        available_models.sort(key=lambda x: ("pro" in x.name, "1.5" in x.name), reverse=True)

        for m_info in available_models:
            try:
                model = genai.GenerativeModel(m_info.name)
                # ทดสอบเรียกใช้สั้นๆ เพื่อป้องกัน Error 404
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, f"เชื่อมต่อสำเร็จ ({m_info.name.split('/')[-1]})"
            except:
                continue # ถ้าติด 404 ให้ไปลองตัวถัดไปในลิสต์
                
        return None, "ไม่พบโมเดลที่ใช้งานได้"
    except Exception as e:
        return None, f"การเชื่อมต่อขัดข้อง: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. ฟังก์ชันเสริมเปรียบเทียบวัสดุ (ใหม่) ---
def render_comparison(material_name):
    st.markdown(f"<div class='comp-box'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#1E3A8A; margin-top:0;'>📊 การเปรียบเทียบวัสดุ: {material_name}</h3>", unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a: st.markdown("**🟢 เกรดมาตรฐาน:** เน้นความคุ้มค่า ได้มาตรฐาน มอก. เหมาะสำหรับงานทั่วไป")
    with c_b: st.markdown("**🏆 เกรดพรีเมียม:** คุณสมบัติสูงพิเศษ (เช่น ทนร้อน/ยืดหยุ่นสูง) แนะนำสำหรับงานโครงสร้างหลัก")
    
    st.markdown("<p style='font-size:0.85rem; margin-top:10px;'>🛒 ตรวจสอบราคาสด (Official Mall):</p>", unsafe_allow_html=True)
    ac1, ac2, ac3 = st.columns(3)
    with ac1: st.markdown(f"<a href='https://shopee.co.th/search?keyword={material_name}&is_official_shop=true' class='aff-btn' target='_blank'>Shopee Mall</a>", unsafe_allow_html=True)
    with ac2: st.markdown(f"<a href='https://www.thaiwatsadu.com/th/search?q={material_name}' class='aff-btn' target='_blank'>Thai Watsadu</a>", unsafe_allow_html=True)
    with ac3: st.markdown(f"<a href='https://www.homepro.co.th/search?q={material_name}' class='aff-btn' target='_blank'>HomePro</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
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
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
# เพิ่ม Story AI
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม คัดสรรวัสดุมาตรฐานสูงสุดเพื่อบ้านที่มั่นคงและปลอดภัย</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนก่อสร้าง", type=['jpg','jpeg','png','pdf'])
    if bp:
        if bp.type == "application/pdf": st.info("📂 รับไฟล์แปลน PDF เรียบร้อย")
        else: st.image(bp)
with c2:
    site = st.file_uploader("📸 สภาพหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 6. LOGIC ---
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            # ปรับ Prompt เพื่อดึงชื่อวัสดุมาเข้าตารางเปรียบเทียบราคา
            prompt = f"วิเคราะห์ฐานะ BHOON KHARN AI โหมด: {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และระบุชื่อวัสดุหลัก 1 อย่างในรูปแบบ [MATERIAL:ชื่อวัสดุ] แนะนำ 3 คำถามขึ้นต้นด้วย 'ถามช่าง: ' แยกบรรทัด"
            inps = [prompt]
            if bp:
                if bp.type == "application/pdf": inps.append({"mime_type": "application/pdf", "data": bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            res = st.session_state.engine.generate_content(inps)
            txt = res.text
            
            raw_qs = re.findall(r"ถามช่าง:\s*(.*)", txt)
            st.session_state.qs = [q.strip() for q in raw_qs if q.strip()][:3]
            st.session_state.rep = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            st.session_state.chat = []
        except Exception as e: st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def ask_more(query):
    if st.session_state.engine:
        res = st.session_state.engine.generate_content(f"BHOON KHARN AI: {query}")
        st.session_state.chat.append({"role": "user", "content": query})
        st.session_state.chat.append({"role": "assistant", "content": res.text})

# --- 7. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพหรือไฟล์แปลน")

if st.session_state.rep:
    st.divider()
    res = st.session_state.rep
    sections = [("🔍 สรุปการวิเคราะห์หน้างาน", "[ANALYSIS]"), ("⏱️ จุดวิกฤตที่ต้องตรวจสอบ", "[RISK]"), ("📝 เทคนิคการตรวจงาน", "[CHECKLIST]"), ("🏗️ มาตรฐานงานวิศวกรรม", "[STANDARD]"), ("🏠 แนะนำสำหรับเจ้าของบ้าน", "[OWNER_NOTE]")]
    
    for title, tag in sections:
        if tag in res:
            content = res.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # แสดงกล่องเปรียบเทียบวัสดุ (ใหม่)
    mat_match = re.search(r"\[MATERIAL:(.*)\]", st.session_state.rep)
    if mat_match:
        render_comparison(mat_match.group(1).strip())

    if st.session_state.qs:
        st.write(""); st.markdown("<p style='font-size:0.85rem; font-weight:bold; color:#1E3A8A;'>💡 ถาม BHOON KHARN AI ต่อ:</p>", unsafe_allow_html=True)
        qcols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if qcols[i].button("🔎 " + qv, key=f"bkq_{i}", use_container_width=True):
                ask_more(qv)

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if ui := st.chat_input("สอบถามเพิ่มเติม..."): ask_more(ui); st.rerun()

    st.markdown(f"<div class='contact-box'><div class='contact-title'>🛠️ รับคำแนะนำจากทีม BHOON KHARN ฟรี</div><div class='contact-info'>📞 โทร: <a href='tel:0887776566' class='contact-link'>088-777-6566</a> | Line: <span class='contact-link'>bhoonkharn</span></div></div>", unsafe_allow_html=True)
    st.markdown("<div class='maroon-note'><strong>หมายเหตุ:</strong> ข้อมูล AI เบื้องต้น ไม่สามารถนำไปใช้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
