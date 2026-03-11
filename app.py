import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE (ยึดตามโทนสีน้ำเงินเดิมของคุณเป๊ะ 100%) ---
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
    
    /* ส่วนเสริม: กล่องเปรียบเทียบวัสดุ */
    .comp-box { border: 1px solid #ddd; border-radius: 12px; padding: 20px; margin-top: 20px; background: #fcfcfc; }
    .aff-btn { display: block; text-align: center; padding: 8px; margin: 5px 0; font-size: 0.8rem; border-radius: 6px; text-decoration: none; border: 1px solid #1E3A8A; color: #1E3A8A; font-weight: bold; }
    .aff-btn:hover { background: #1E3A8A; color: white; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ปรับเป็น: ค้นหาตัวใหม่ที่สุดก่อนเสมอตามสั่ง) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "กรุณาตั้งค่า API Key"
    
    try:
        genai.configure(api_key=api_key)
        # ขั้นตอนที่ 1: ดึงลิสต์โมเดลที่รองรับทั้งหมด
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        # ขั้นตอนที่ 2: เรียงลำดับเพื่อให้ Pro อยู่ก่อน Flash และรุ่นใหม่ (เช่น 1.5) อยู่ก่อนรุ่นเก่า
        # เราจะเรียงแบบ Reverse เพื่อให้ชื่อที่ใหม่กว่า/สเปกสูงกว่าขึ้นมาเลือกก่อน
        available_models.sort(reverse=True)

        # ขั้นตอนที่ 3: วนลูปทดสอบเพื่อเลือกตัวที่ดีที่สุดที่ใช้งานได้จริง (ป้องกัน 404)
        for model_name in available_models:
            try:
                model = genai.GenerativeModel(model_name)
                # ทดสอบเรียกสั้นๆ เพื่อเช็กสถานะ
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, f"เชื่อมต่อสำเร็จ ({model_name.split('/')[-1]})"
            except:
                continue # ถ้าตัวนี้ 404 หรือมีปัญหา ให้ไปลองตัวถัดไปในลิสต์
                
        return None, "ไม่พบโมเดลที่พร้อมใช้งาน"
    except Exception as e:
        return None, f"การเชื่อมต่อขัดข้อง: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. ฟังก์ชันเสริมเปรียบเทียบวัสดุ ---
def render_comparison(material_name):
    st.markdown(f"<div class='comp-box'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#1E3A8A; margin-top:0;'>📊 เปรียบเทียบวัสดุ: {material_name}</h3>", unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a: st.markdown("**🟢 เกรดมาตรฐาน:** คุ้มค่า ได้มาตรฐาน มอก. เหมาะสำหรับงานทั่วไป")
    with c_b: st.markdown("**🏆 เกรดพรีเมียม:** คุณสมบัติสูงกว่า (เช่น ทนทานพิเศษ) อายุการใช้งานยาวนาน")
    
    st.markdown("<p style='font-size:0.85rem; margin-top:10px;'>🛒 ตรวจสอบราคาสด (ร้านค้าทางการ):</p>", unsafe_allow_html=True)
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
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม คัดสรรวัสดุมาตรฐานสูงสุดเพื่อความมั่นใจในทุกขั้นตอนการสร้างบ้าน</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แปลนก่อสร้าง", type=['jpg','jpeg','png','pdf'])
    if bp:
        if bp.type == "application/pdf": st.info("📂 รับไฟล์แปลน PDF เรียบร้อย")
        else: st.image(bp)
with c2:
    site = st.file_uploader("📸 สภาพหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 6. LOGIC & DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if not (bp or site):
        st.warning("กรุณาอัปโหลดรูปภาพ")
    else:
        with st.spinner("AI กำลังวิเคราะห์ข้อมูล..."):
            try:
                # ปรับ Prompt เพื่อดึงชื่อวัสดุมาใช้งาน
                prompt = f"วิเคราะห์ภาพโหมด {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และระบุชื่อวัสดุหลักท้ายรายงานในรูปแบบ [MATERIAL:ชื่อวัสดุ]"
                inps = [prompt]
                if bp:
                    if bp.type == "application/pdf": inps.append({"mime_type":"application/pdf","data":bp.getvalue()})
                    else: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                
                res = st.session_state.engine.generate_content(inps)
                st.session_state.rep = res.text
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")

if st.session_state.rep:
    st.divider()
    sections = [("🔍 สรุปผลการวิเคราะห์", "[ANALYSIS]"), ("⚠️ จุดวิกฤต", "[RISK]"), ("📝 เทคนิคการตรวจ", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 แนะนำเจ้าของบ้าน", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # ระบบเปรียบเทียบวัสดุ (ส่วนเสริมใหม่)
    mat_match = re.search(r"\[MATERIAL:(.*)\]", st.session_state.rep)
    if mat_match:
        render_comparison(mat_match.group(1).strip())

    st.markdown(f"<div style='text-align:center; margin-top:30px; border-top:1px solid #eee; padding-top:20px; font-size:0.85rem; color:#8B0000;'>หมายเหตุ: ข้อมูล AI เบื้องต้น ไม่สามารถใช้อ้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
