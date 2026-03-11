import streamlit as st, google.generativeai as genai, re
from PIL import Image

# --- 1. CONFIG & CSS (พรีเมียม น้ำตาล-ทอง, ขนาดตัวอักษรเล็กคมชัด) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-dark: #4A3F35; }
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.5; font-size: 0.9rem; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 1.8rem; margin-bottom: 0; }
    .story-text { text-align: center; color: var(--bk-dark); font-size: 0.8rem; margin-bottom: 25px; opacity: 0.8; padding: 0 12%; line-height: 1.4; }
    .section-header { color: var(--bk-gold); font-size: 0.95rem; font-weight: 700; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 20px; }
    .owner-content { border-left: 3px solid var(--bk-gold); padding-left: 15px; margin: 10px 0; white-space: pre-line; font-size: 0.85rem; background: #FCFAFA; padding: 10px; }
    div.stButton > button { font-size: 0.75rem !important; border: 1px solid var(--bk-gold) !important; color: var(--bk-gold) !important; background: transparent; border-radius: 4px; }
    div.stButton > button:hover { background: var(--bk-gold) !important; color: white !important; }
    .comp-box { border: 1px solid #eee; border-radius: 8px; padding: 12px; margin-top: 10px; background: #FFF; }
    .aff-btn { display: block; text-align: center; padding: 6px; margin: 4px 0; font-size: 0.7rem; border-radius: 4px; text-decoration: none; border: 1px solid #ddd; color: #555; font-weight: bold; }
    .aff-btn:hover { border-color: var(--bk-gold); color: var(--bk-gold); }
</style>""", unsafe_allow_html=True)

# --- 2. PLUGIN FUNCTIONS (ส่วนเสริม: เปรียบเทียบวัสดุและเกรด) ---
def render_material_comparison(material_name):
    """ฟังก์ชันแสดงตารางเปรียบเทียบราคาและคุณสมบัติ (ส่วนเสริมใหม่)"""
    st.markdown(f"<div class='comp-box'>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:var(--bk-gold); font-weight:bold; margin-bottom:5px;'>📊 เจาะลึกและเปรียบเทียบวัสดุ: {material_name}</p>", unsafe_allow_html=True)
    
    # วิเคราะห์ความต่างของเกรด
    c_a, c_b = st.columns(2)
    with c_a: 
        st.markdown("<p style='font-size:0.75rem; color:#666;'><b>🟢 เกรดมาตรฐาน:</b><br>เน้นความคุ้มค่า ได้มาตรฐาน มอก. เหมาะสำหรับงานทั่วไป</p>", unsafe_allow_html=True)
    with c_b: 
        st.markdown("<p style='font-size:0.75rem; color:#666;'><b>🏆 เกรดพรีเมียม:</b><br>ทนทานสูง มีคุณสมบัติพิเศษเฉพาะทาง อายุการใช้งานยาวนานกว่า</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.7rem; margin-top:5px; color:var(--bk-dark); opacity:0.7;'>🛒 ตรวจสอบราคาสด (Official Mall เท่านั้น):</p>", unsafe_allow_html=True)
    
    # ปุ่มเปรียบเทียบ 3 ร้าน (รองรับ Affiliate ID ในอนาคต)
    ac1, ac2, ac3 = st.columns(3)
    with ac1: st.markdown(f"<a href='https://shopee.co.th/search?keyword={material_name}&is_official_shop=true' class='aff-btn' target='_blank'>Shopee Mall</a>", unsafe_allow_html=True)
    with ac2: st.markdown(f"<a href='https://www.thaiwatsadu.com/th/search?q={material_name}' class='aff-btn' target='_blank'>Thai Watsadu</a>", unsafe_allow_html=True)
    with ac3: st.markdown(f"<a href='https://www.homepro.co.th/search?q={material_name}' class='aff-btn' target='_blank'>HomePro</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 3. ENGINE & INITIALIZATION (คงเดิม) ---
def init_ai():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "Offline"
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("models/gemini-1.5-flash"), "Ready"
    except: return None, "Error"

if "model" not in st.session_state: st.session_state.model, st.session_state.status = init_ai()
for s in ["chat", "rep", "qs"]: 
    if s not in st.session_state: st.session_state[s] = [] if s != "rep" else ""

# --- 4. SIDEBAR (เพิ่มช่อง Supabase History) ---
with st.sidebar:
    st.markdown("### BHOON KHARN")
    st.caption(f"System: {st.session_state.status}")
    st.divider()
    st.markdown("**Member History**")
    st.text_input("Customer ID", placeholder="Coming Soon (Supabase)", disabled=True)
    st.divider()
    mode = st.radio("Analysis Mode:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []; st.rerun()

# --- 5. HEADER & STORY ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("<div class='story-text'>ยกระดับการตรวจงานก่อสร้างด้วย AI วิศวกรรมที่แม่นยำที่สุด ช่วยเจ้าของบ้านคัดเลือกวัสดุมาตรฐานสูงสุดจากร้านค้าทางการ เพื่อความมั่นใจในทุกขั้นตอนการสร้างบ้าน</div>", unsafe_allow_html=True)

# --- 6. UPLOAD & PROCESSING ---
c1, c2 = st.columns(2)
with c1: 
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2: 
    site = st.file_uploader("📸 หน้างานจริง", type=['jpg','jpeg','png'])
    if site: st.image(site)

if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if not (bp or site): st.warning("กรุณาอัปโหลดไฟล์")
    else:
        with st.spinner("AI กำลังวิเคราะห์มาตรฐานวิศวกรรม..."):
            try:
                # Prompt ที่สั่งให้ AI สกัดชื่อวัสดุมาด้วยเพื่อใช้ในระบบเปรียบเทียบ
                prompt = f"โหมด: {mode} วิเคราะห์จากภาพ หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] (และแนะนำงานขั้นตอนถัดไป) ระบุชื่อวัสดุหลัก 1 อย่างท้ายรายงานด้วย Tag [MATERIAL:ชื่อวัสดุ] และแนะนำคำถาม 3 ข้อ 'ถามช่าง: '"
                inps = [prompt]
                if bp: 
                    if bp.type == "application/pdf": inps.append({"mime_type":"application/pdf","data":bp.getvalue()})
                    else: inps.append(Image.open(bp))
                if site: inps.append(Image.open(site))
                res = st.session_state.model.generate_content(inps)
                st.session_state.rep = res.text
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", res.text)[:3]]
            except Exception as e: st.error(f"Error: {e}")

# --- 7. DISPLAY RESULTS ---
if st.session_state.rep:
    st.divider()
    sections = [("🔍 สรุปผลการวิเคราะห์", "[ANALYSIS]"), ("⚠️ จุดวิกฤต/ความเสี่ยง", "[RISK]"), ("📝 เทคนิคการตรวจงาน", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 แนะนำเจ้าของบ้าน & งานอนาคต", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # ดึงชื่อวัสดุมาเข้า Plugin เปรียบเทียบราคา
    mat_match = re.search(r"\[MATERIAL:(.*)\]", st.session_state.rep)
    target_material = mat_match.group(1).strip() if mat_match else "วัสดุก่อสร้าง"
    render_material_comparison(target_material)

    # ปุ่มคำถามแนะนำ
    if st.session_state.qs:
        st.write(""); st.markdown("<p style='font-size:0.8rem; font-weight:bold; color:var(--bk-gold);'>💡 ถามต่อ:</p>", unsafe_allow_html=True)
        qcols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if qcols[i].button(qv, key=f"bkq_{i}", use_container_width=True): 
                # ฟังก์ชันถาม AI ต่อ (จำลองการทำงาน)
                st.info(f"กำลังหาคำตอบสำหรับ: {qv}")

    # ช่องทางติดต่อท้ายรายงาน
    st.markdown(f"<div style='border-top:1px solid #eee; margin-top:30px; padding-top:20px; text-align:center;'><p style='color:var(--bk-gold); font-weight:700;'>🛠️ ปรึกษาทีมวิศวกร BHOON KHARN ฟรี</p><p style='font-size:0.8rem;'>📞 088-777-6566 | Line: @bhoonkharn</p></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.7rem; color:maroon; opacity:0.6;'>หมายเหตุ: ข้อมูล AI เป็นเพียงคำแนะนำเบื้องต้น ไม่สามารถใช้อ้างอิงทางกฎหมายได้</p>", unsafe_allow_html=True)
