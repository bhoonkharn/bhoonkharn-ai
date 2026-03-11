import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE (ยึดตามโทนสีน้ำเงินและฟอนต์ Sarabun ของคุณ) ---
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
    .comp-box { border: 1px solid #ddd; border-radius: 12px; padding: 20px; margin-top: 20px; background: #fcfcfc; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .aff-btn { display: block; text-align: center; padding: 8px; margin: 5px 0; font-size: 0.8rem; border-radius: 6px; text-decoration: none; border: 1px solid #1E3A8A; color: #1E3A8A; font-weight: bold; }
    .aff-btn:hover { background: #1E3A8A; color: white; }
</style>
""", unsafe_allow_html=True)

# --- 2. DYNAMIC ENGINE (ค้นหาตัวใหม่และฉลาดที่สุดก่อนเสมอ) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "กรุณาตั้งค่า API Key ใน Secrets"
    
    try:
        genai.configure(api_key=api_key)
        # สแกนหาโมเดลทั้งหมดที่รองรับ generateContent
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        # เรียงลำดับโมเดล: Pro จะถูกเลือกก่อน Flash และรุ่นที่เลขเวอร์ชั่นสูงกว่าจะถูกเลือกก่อน
        # การ Sort แบบ reverse โดยปกติจะเอา 'gemini-1.5-pro' ขึ้นก่อน 'gemini-1.5-flash'
        available_models.sort(reverse=True)

        for m_name in available_models:
            try:
                # ทดสอบเรียกใช้โมเดลที่เลือกมา
                test_model = genai.GenerativeModel(m_name)
                test_model.generate_content("hi", generation_config={"max_output_tokens": 1})
                return test_model, f"เชื่อมต่อสำเร็จ: {m_name.split('/')[-1]}"
            except:
                continue # ถ้าติด 404 หรือปัญหาอื่นๆ ให้ลองตัวถัดไปในลิสต์ทันที
                
        return None, "ไม่พบโมเดลที่รองรับในบัญชีของคุณ"
    except Exception as e:
        return None, f"การเชื่อมต่อขัดข้อง: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

if "chat" not in st.session_state: st.session_state.chat = []
if "rep" not in st.session_state: st.session_state.rep = ""
if "qs" not in st.session_state: st.session_state.qs = []

# --- 3. ฟังก์ชันเสริม: กล่องเปรียบเทียบราคาวัสดุ ---
def render_comparison(material_name):
    st.markdown(f"<div class='comp-box'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#1E3A8A; margin-top:0;'>📊 การเปรียบเทียบวัสดุ: {material_name}</h3>", unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a: st.markdown("**🟢 เกรดมาตรฐาน:** เน้นความคุ้มค่า ได้มาตรฐาน มอก. เหมาะสำหรับงานทั่วไป")
    with c_b: st.markdown("**🏆 เกรดพรีเมียม:** คุณสมบัติสูงพิเศษ อายุการใช้งานยาวนาน (แนะนำสำหรับงานโครงสร้าง)")
    
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
    
    if st.button("🔄 รีเซ็ตระบบ AI", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    
    mode = st.radio("มุมมองการวิเคราะห์:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    
    if st.button("🗑️ ล้างประวัติงานตรวจ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# --- 5. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
# เพิ่ม Story AI เพื่อความว้าว
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม คัดสรรวัสดุมาตรฐานสูงสุดเพื่อบ้านที่มั่นคงและปลอดภัยในระยะยาว</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 ไฟล์แปลน (PDF/Image)", type=['jpg','jpeg','png','pdf'])
    if bp:
        if bp.type == "application/pdf": st.info("📂 ระบบรับไฟล์แปลน PDF เรียบร้อย")
        else: st.image(bp)
with c2:
    site = st.file_uploader("📸 รูปถ่ายหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 6. LOGIC & DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if not (bp or site):
        st.warning("กรุณาอัปโหลดรูปภาพก่อนเริ่มงาน")
    else:
        with st.spinner("AI กำลังเลือกวัสดุและวิเคราะห์มาตรฐานวิศวกรรม..."):
            try:
                # ปรับ Prompt เพื่อสกัดชื่อวัสดุมาเข้าตารางเปรียบเทียบราคา
                prompt = f"วิเคราะห์ภาพโหมด {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และระบุชื่อวัสดุหลัก 1 อย่างท้ายรายงานในรูปแบบ [MATERIAL:ชื่อวัสดุ]"
                inps = [prompt]
                if bp:
                    if bp.type == "application/pdf": inps.append({"mime_type":"application/pdf","data":bp.getvalue()})
                    else: inps.append(Image.open(bp))
                if site: inps.append(Image.append(site) if hasattr(Image, "append") else Image.open(site))
                
                res = st.session_state.engine.generate_content(inps)
                st.session_state.rep = res.text
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")

if st.session_state.rep:
    st.divider()
    sections = [("🔍 ผลการวิเคราะห์", "[ANALYSIS]"), ("⚠️ จุดเสี่ยงวิกฤต", "[RISK]"), ("📝 เทคนิคการตรวจงาน", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 คำแนะนำสำหรับเจ้าของบ้าน", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # ดึงชื่อวัสดุมาเข้า Plugin เปรียบเทียบราคา (ส่วนเสริม)
    mat_match = re.search(r"\[MATERIAL:(.*)\]", st.session_state.rep)
    if mat_match:
        render_comparison(mat_match.group(1).strip())

    st.markdown(f"<div style='text-align:center; margin-top:30px; border-top:1px solid #eee; padding-top:20px; font-size:0.85rem; color:#8B0000;'>หมายเหตุ: ข้อมูล AI เป็นเพียงคำแนะนำเบื้องต้น ไม่สามารถใช้อ้างอิงทางกฎหมายได้</div>", unsafe_allow_html=True)
