import streamlit as st, google.generativeai as genai, re
from PIL import Image

# --- 1. CONFIG & STYLE (Official & Premium Tone) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    :root { --bk-gold: #B59473; --bk-dark: #4A3F35; }
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; line-height: 1.6; font-size: 0.9rem; }
    .main-title { color: var(--bk-gold); text-align: center; font-weight: 700; font-size: 1.8rem; margin-bottom: 0; }
    .story-text { text-align: center; color: var(--bk-dark); font-size: 0.8rem; margin-bottom: 30px; opacity: 0.8; padding: 0 10%; }
    .section-header { color: var(--bk-gold); font-size: 1rem; font-weight: 700; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 25px; }
    .owner-content { border-left: 3px solid var(--bk-gold); padding-left: 15px; margin: 15px 0; white-space: pre-line; font-size: 0.9rem; }
    div.stButton > button { font-size: 0.75rem !important; border: 1px solid var(--bk-gold) !important; color: var(--bk-gold) !important; background: transparent; border-radius: 4px; }
    div.stButton > button:hover { background: var(--bk-gold) !important; color: white !important; }
    
    /* เพิ่ม Style สำหรับกล่องเปรียบเทียบวัสดุ */
    .comp-box { border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-top: 15px; background: #FFF; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .aff-btn { display: block; text-align: center; padding: 8px; margin: 5px 0; font-size: 0.75rem; border-radius: 4px; text-decoration: none; border: 1px solid #ddd; color: #555; font-weight: bold; }
    .aff-btn:hover { border-color: var(--bk-gold); color: var(--bk-gold); }
</style>""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันเสริมสำหรับการเปรียบเทียบวัสดุ (เพิ่มใหม่) ---
def render_material_comparison(material_name):
    st.markdown(f"<div class='comp-box'>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:var(--bk-gold); font-weight:bold; margin-bottom:10px;'>📊 เปรียบเทียบวัสดุและคุณสมบัติ: {material_name}</p>", unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a: st.markdown("<p style='font-size:0.8rem;'><b>🟢 เกรดมาตรฐาน:</b> เน้นความคุ้มค่า ได้มาตรฐาน มอก. เหมาะสำหรับงานทั่วไป</p>", unsafe_allow_html=True)
    with c_b: st.markdown("<p style='font-size:0.8rem;'><b>🏆 เกรดพรีเมียม:</b> มีสารเพิ่มประสิทธิภาพ ทนทานสูงกว่า อายุการใช้งานยาวนาน</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.75rem; margin-top:10px; color:#666;'>🛒 ตรวจสอบราคาสด (ร้านค้าทางการ):</p>", unsafe_allow_html=True)
    ac1, ac2, ac3 = st.columns(3)
    with ac1: st.markdown(f"<a href='https://shopee.co.th/search?keyword={material_name}&is_official_shop=true' class='aff-btn' target='_blank'>Shopee Mall</a>", unsafe_allow_html=True)
    with ac2: st.markdown(f"<a href='https://www.thaiwatsadu.com/th/search?q={material_name}' class='aff-btn' target='_blank'>Thai Watsadu</a>", unsafe_allow_html=True)
    with ac3: st.markdown(f"<a href='https://www.homepro.co.th/search?q={material_name}' class='aff-btn' target='_blank'>HomePro</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 3. ENGINE (แก้ไขชื่อโมเดลเพื่อแก้ Error 404) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "No API Key"
    try:
        genai.configure(api_key=api_key)
        # แก้ไข: ตัด models/ ออกเพื่อให้รองรับ v1beta ได้เสถียรขึ้น
        model = genai.GenerativeModel("gemini-1.5-flash")
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        return model, "Ready"
    except:
        try:
            # Fallback: ค้นหาตัวที่รองรับอัตโนมัติหากตัวหลักมีปัญหา
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods: return genai.GenerativeModel(m.name), "Ready"
        except: pass
        return None, "Offline"

if "engine" not in st.session_state: st.session_state.engine, st.session_state.status = init_ai_engine()
for s in ["chat", "rep", "qs"]: 
    if s not in st.session_state: st.session_state[s] = [] if s != "rep" else ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN")
    st.caption(f"Status: {st.session_state.status}")
    st.divider()
    st.markdown("**Member Area (Coming Soon)**")
    user_id = st.text_input("Customer ID", placeholder="กรอกเลขสมาชิกเพื่อดูประวัติ", disabled=True)
    st.info("ระบบ Supabase History กำลังพัฒนา")
    st.divider()
    mode = st.radio("Mode:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []; st.rerun()

# --- 5. MAIN UI ---
st.markdown("<div class='main-title'>BHOON KHARN AI</div>", unsafe_allow_html=True)
st.markdown("""<div class='story-text'>
    ขับเคลื่อนด้วยวิศวกรรม AI ที่วิเคราะห์ข้อมูลจากมาตรฐานงานก่อสร้างระดับสากล 
    ผสมผสานกับประสบการณ์จริงจากทีม BHOON KHARN เพื่อความแม่นยำและปลอดภัยสูงสุดในทุกตารางเมตร
</div>""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: 
    bp = st.file_uploader("📋 แปลน (PDF/JPG)", type=['jpg','jpeg','png','pdf'])
    if bp and bp.type != "application/pdf": st.image(bp)
with c2: 
    site = st.file_uploader("📸 หน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site)

# --- 6. LOGIC ---
def run_analysis():
    if not st.session_state.engine: return
    with st.spinner("AI กำลังวิเคราะห์ข้อมูลระดับวิศวกรรม..."):
        try:
            # ปรับ Prompt เล็กน้อยเพื่อสกัดชื่อวัสดุ
            prompt = f"วิเคราะห์ภาพฐานะ BHOON KHARN AI โหมด: {mode} หัวข้อ: [ANALYSIS], [RISK], [CHECKLIST], [STANDARD], [OWNER_NOTE] ระบุชื่อวัสดุหลัก 1 อย่างที่จำเป็นในรูปแบบ [MATERIAL:ชื่อวัสดุ] แนะนำ 3 คำถามขึ้นต้นด้วย 'ถามช่าง: ' แยกบรรทัด"
            inps = [prompt]
            if bp: 
                if bp.type == "application/pdf": inps.append({"mime_type":"application/pdf","data":bp.getvalue()})
                else: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            res = st.session_state.engine.generate_content(inps)
            st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", res.text)[:3]]
            st.session_state.rep = re.sub(r"ถามช่าง:.*", "", res.text, flags=re.DOTALL).strip()
            st.session_state.chat = []
        except Exception as e: st.error(str(e))

def ask_more(query):
    if st.session_state.engine:
        res = st.session_state.engine.generate_content(f"BHOON KHARN AI: {query}")
        st.session_state.chat.append({"role": "user", "content": query}); st.session_state.chat.append({"role": "assistant", "content": res.text})

# --- 7. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพ")

if st.session_state.rep:
    st.divider()
    sections = [("🔍 สรุปผลการวิเคราะห์", "[ANALYSIS]"), ("⏱️ จุดวิกฤต", "[RISK]"), ("📝 เทคนิคการตรวจ", "[CHECKLIST]"), ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 เจ้าของบ้าน & อนาคต", "[OWNER_NOTE]")]
    for title, tag in sections:
        if tag in st.session_state.rep:
            content = st.session_state.rep.split(tag)[1].split("[")[0].strip()
            st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
            if tag == "[OWNER_NOTE]": st.markdown(f"<div class='owner-content'>{content}</div>", unsafe_allow_html=True)
            else: st.write(content)
    
    # แสดงกล่องเปรียบเทียบวัสดุ (Plugin ใหม่)
    mat_match = re.search(r"\[MATERIAL:(.*)\]", st.session_state.rep)
    if mat_match:
        render_material_comparison(mat_match.group(1).strip())

    if st.session_state.qs:
        st.write(""); st.markdown("<p style='font-size:0.8rem; font-weight:bold; color:var(--bk-gold);'>💡 ถามต่อ:</p>", unsafe_allow_html=True)
        qcols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if qcols[i].button(qv, key=f"bkq_{i}", use_container_width=True): ask_more(qv); st.rerun()

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if ui := st.chat_input("สอบถามเพิ่มเติม..."): ask_more(ui); st.rerun()

    st.markdown(f"<div style='border-top:1px solid #eee; margin-top:40px; padding:20px 0; text-align:center;'><div style='color:var(--bk-gold); font-weight:700; font-size:1rem; margin-bottom:10px;'>🛠️ รับคำแนะนำฟรีจากทีม BHOON KHARN</div><div style='font-size:0.9rem;'>📞 <a href='tel:0887776566' style='color:var(--bk-gold);'>088-777-6566</a> | 💬 Line: <a href='https://line.me/ti/p/~bhoonkharn' style='color:var(--bk-gold);'>bhoonkharn</a></div></div>", unsafe_allow_html=True)
