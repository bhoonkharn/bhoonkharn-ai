import streamlit as st, google.generativeai as genai, re
from PIL import Image

# --- 1. CONFIG & CSS (พรีเมียม น้ำตาล-ทอง) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-dark: #4A3F35; }
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.5; font-size: 0.9rem; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 1.8rem; margin-bottom: 0; }
    .story-text { text-align: center; color: var(--bk-dark); font-size: 0.8rem; margin-bottom: 25px; opacity: 0.8; padding: 0 12%; }
    .section-header { color: var(--bk-gold); font-size: 0.95rem; font-weight: 700; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 20px; }
    .owner-content { border-left: 3px solid var(--bk-gold); padding-left: 15px; margin: 10px 0; white-space: pre-line; font-size: 0.85rem; background: #FCFAFA; padding: 10px; }
    div.stButton > button { font-size: 0.75rem !important; border: 1px solid var(--bk-gold) !important; color: var(--bk-gold) !important; background: transparent; }
    .comp-box { border: 1px solid #eee; border-radius: 8px; padding: 12px; margin-top: 10px; background: #FFF; }
    .aff-btn { display: block; text-align: center; padding: 6px; margin: 4px 0; font-size: 0.7rem; border-radius: 4px; text-decoration: none; border: 1px solid #ddd; color: #555; font-weight: bold; }
</style>""", unsafe_allow_html=True)

# --- 2. AUXILIARY FUNCTIONS ---
def render_comparison(material_name):
    st.markdown(f"<div class='comp-box'>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:var(--bk-gold); font-weight:bold;'>📊 เปรียบเทียบวัสดุ: {material_name}</p>", unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a: st.markdown("<p style='font-size:0.75rem;'><b>🟢 มาตรฐาน:</b> คุ้มค่า ได้ มอก.</p>", unsafe_allow_html=True)
    with c_b: st.markdown("<p style='font-size:0.75rem;'><b>🏆 พรีเมียม:</b> ทนทานพิเศษ เกรดสูงสุด</p>", unsafe_allow_html=True)
    ac1, ac2, ac3 = st.columns(3)
    with ac1: st.markdown(f"<a href='https://shopee.co.th/search?keyword={material_name}&is_official_shop=true' class='aff-btn' target='_blank'>Shopee Mall</a>", unsafe_allow_html=True)
    with ac2: st.markdown(f"<a href='https://www.thaiwatsadu.com/th/search?q={material_name}' class='aff-btn' target='_blank'>Thai Watsadu</a>", unsafe_allow_html=True)
    with ac3: st.markdown(f"<a href='https://www.homepro.co.th/search?q={material_name}' class='aff-btn' target='_blank'>HomePro</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 3. CORE ENGINE (แก้ไขจุด Error 404: เลือกตัวที่รองรับและใหม่ที่สุด) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "No API Key"
    try:
        genai.configure(api_key=api_key)
        # กรองเฉพาะโมเดลที่รองรับ generateContent และเรียงลำดับจากใหม่ไปเก่า
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        # ค้นหาตัวที่ใหม่กว่า 1.5-flash ถ้ามี หรือใช้ 1.5-flash ตัวที่ถูกต้อง
        target_model = "models/gemini-1.5-flash" # Default
        for m in sorted(available_models, reverse=True):
            if "1.5" in m: # เน้นตระกูล 1.5 ที่เสถียรและใหม่
                target_model = m
                break
        return genai.GenerativeModel(target_model), "Ready"
    except Exception as e:
        return None, f"Offline: {str(e)}"

if "engine" not in st.session_state: st.session_state.engine, st.session_state.status = init_ai_engine()
for s in ["chat", "rep", "qs"]: 
    if s not in st.session_state: st.session_state[s] = [] if s != "rep" else ""

# --- 4. SIDEBAR & HEADER ---
with st.sidebar:
    st.markdown("### BHOON KHARN")
    st.caption(f"Status: {st.session_state.status}")
    st.divider()
    st.text_input("Customer ID (Supabase)", placeholder="Coming Soon", disabled=True)
    mode = st.radio("Mode:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []; st.rerun()

st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>วิเคราะห์งานก่อสร้างด้วย AI วิศวกรรม คัดสรรวัสดุมาตรฐานจากร้านค้าทางการเพื่อความมั่นใจสูงสุด</div>", unsafe_allow_html=True)

# --- 5. UPLOAD & PROCESSING ---
c1, c2 = st.columns(2)
with c1: 
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2: 
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if not (bp or site): st.warning("กรุณาอัปโหลดรูปภาพ")
    else:
        with st.spinner("Analyzing..."):
            try:
                prompt = f"วิเคราะห์จากภาพโหมด {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] และระบุชื่อวัสดุหลักท้ายรายงานในรูปแบบ [MATERIAL:ชื่อวัสดุ]"
                inps = [prompt]
                if bp: 
                    if bp.type == "application/pdf": inps.append({"mime_type":"application/pdf","data":bp.getvalue()})
                    else: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                res = st.session_state.engine.generate_content(inps)
                st.session_state.rep = res.text
            except Exception as e: st.error(str(e))

# --- 6. DISPLAY RESULTS ---
if st.session_state.rep:
    st.divider()
    sections = [("🔍 วิเคราะห์", "[ANALYSIS]"), ("⚠️ ความเสี่ยง", "[RISK]"), ("📝 เทคนิคการตรวจ", "[CHECKLIST]"), ("🏗️ มาตรฐาน", "[STANDARD]"), ("🏠 แนะนำเจ้าของบ้าน", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    mat_match = re.search(r"\[MATERIAL:(.*)\]", st.session_state.rep)
    render_comparison(mat_match.group(1) if mat_match else "วัสดุก่อสร้าง")

    st.markdown(f"<div style='text-align:center; margin-top:30px; border-top:1px solid #eee; padding-top:20px;'>🛠️ ปรึกษาฟรี: 088-777-6566 | Line: @bhoonkharn</div>", unsafe_allow_html=True)
