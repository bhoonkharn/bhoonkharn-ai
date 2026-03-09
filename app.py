import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# โค้ด CSS เพื่อล็อกตำแหน่งและปรับแต่งความสวยงาม
st.markdown("""
    <style>
    #report-header {
        scroll-margin-top: 100px;
    }
    .main-disclaimer {
        font-size: 0.85rem;
        color: #666;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการ API Key
def get_working_keys():
    keys = []
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "GOOGLE_API_KEY" in k and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "ไม่พบ API Key"
    shuffled = keys.copy()
    random.shuffle(shuffled)
    for k in shuffled:
        try:
            genai.configure(api_key=k)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0] if models else None
            if not target: continue
            model = genai.GenerativeModel(target)
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    engine, status = init_engine(get_working_keys())
    st.session_state.engine = engine
    st.session_state.status = status

# ระบบ Session ข้อมูล
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. แถบเครื่องมือด้านซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if st.session_state.engine: st.success("🟢 ระบบพร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status', 'ขัดข้อง')}")
    
    if st.button("🔄 รีเซ็ตระบบ"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดและพรีวิวรูปภาพ
col_l, col_r = st.columns(2)
with col_l:
    blueprint = st.file_uploader("📋 อัปโหลดแบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
    if blueprint: st.image(blueprint, caption="แบบอ้างอิง", use_container_width=True)
with col_r:
    site_photo = st.file_uploader("📸 อัปโหลดภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_photo: st.image(site_photo, caption="หน้างานจริง", use_container_width=True)

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site_photo or blueprint:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                prompt = f"""
                คุณคือที่ปรึกษา BHOON KHARN AI 
                วิเคราะห์ภาพก่อสร้างโดยเริ่มทันทีที่หัวข้อแรก:
                🔍 [วิเคราะห์หน้างาน]: (หากภาพไม่ชัด ให้แจ้งเตือนทันทีและขอให้ถ่ายใหม่)
                ⏱️ [จุดตายวิกฤต]: (วิเคราะห์ความเสี่ยงแฝง)
                ⚠️ [ผลกระทบต่อเนื่อง]: (Domino Effect และงบซ่อม)
                🏗️ [มาตรฐานเทคนิค]: (วสท./สากล)
                🏠 [วิธีเช็คเอง 1-2-3]: (ขั้นตอนง่ายๆ)
                แนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:' (ห้ามแสดงหัวข้อคำถามในเนื้อหา)
                โหมด: {mode}
                """
                imgs = [Image.open(f) for f in [blueprint, site_photo] if f]
                resp = st.session_state.engine.generate_content([prompt] + imgs)
                full_text = resp.text
                
                # เก็บคำถามและลบออกจากเนื้อหาหลัก
                found_qs = re.findall(r"ถามช่าง: (.+)", full_text)
                st.session_state.quick_qs = [q.strip() for q in found_qs[:3]]
                clean_report = re.sub(r"ถามช่าง: .*", "", full_text).strip()
                
                st.session_state.final_report = clean_report
                st.session_state.chat_history = [{"role": "assistant", "content": clean_report}]
                # ไม่ใช้ st.rerun() เพื่อป้องกันหน้าจอเด้งไปล่างสุด
            except Exception as e: st.error(f"ผิดพลาด: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# --- 6. ส่วนการแสดงผล (จัดลำดับให้อ่านจากบนลงล่าง) ---

if st.session_state.final_report:
    # จุด Anchor สำหรับเลื่อนขึ้นมาอ่าน
    st.markdown('<div id="report-header"></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📋 ผลการตรวจสอบและวิเคราะห์")
    
    # แสดงรายงานแบบ Smart (Expanders)
    text = st.session_state.final_report
    patterns = {
        "🔍 วิเคราะห์หน้างาน": r"🔍 \[วิเคราะห์หน้างาน\]:(.*?)(?=⏱️|⚠️|🏗️|🏠|$)",
        "⏱️ จุดตายวิกฤต": r"⏱️ \[จุดตายวิกฤต\]:(.*?)(?=⚠️|🏗️|🏠|$)",
        "⚠️ ผลกระทบต่อเนื่อง": r"⚠️ \[ผลกระทบต่อเนื่อง\]:(.*?)(?=🏗️|🏠|$)",
        "🏗️ มาตรฐานเทคนิค": r"🏗️ \[มาตรฐานเทคนิค\]:(.*?)(?=🏠|$)",
        "🏠 วิธีเช็คเอง 1-2-3": r"🏠 \[วิธีเช็คเอง 1-2-3\]:(.*?)$"
    }
    
    for title, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            if "🔍" in title:
                st.info(content)
            else:
                with st.expander(f"**{title}**"):
                    st.markdown(content)
    
    st.download_button("📥 บันทึกรายงาน (TXT)", st.session_state.final_report, "BK_Analysis.txt")

    # ปุ่มคำถามด่วน (Quick Reply) - วางไว้ใต้รายงานทันที
    if st.session_state.quick_qs:
        st.markdown("##### 💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:")
        cols = st.columns(len(st.session_state.quick_qs))
        for idx, q in enumerate(st.session_state.quick_qs):
            if cols[idx].button(f"🔎 {q}", key=f"q_{idx}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                res = st.session_state.engine.generate_content(f"วิเคราะห์ในฐานะ BHOON KHARN: {q}")
                st.session_state.chat_history.append({"role": "assistant", "content": res.text})
                st.rerun()

    # แสดงประวัติแชทที่คุยต่อ
    if len(st.session_state.chat_history) > 1:
        st.divider()
        for msg in st.session_state.chat_history[1:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ช่องแชทอิสระ
    if user_q := st.chat_input("พิมพ์คำถามอื่นๆ..."):
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        res = st.session_state.engine.generate_content(f"วิเคราะห์ในฐานะ BHOON KHARN: {user_q}")
        st.session_state.chat_history.append({"role": "assistant", "content": res.text})
        st.rerun()
    
    # 7. หมายเหตุแบบทางการ (Formal Disclaimer)
    st.markdown(f"""
    <div class="main-disclaimer">
        <strong>ข้อกำหนดและขอบเขตความรับผิดชอบ (Disclaimer):</strong><br>
        1. ข้อมูลนี้เป็นการวิเคราะห์เบื้องต้นโดยระบบ BHOON KHARN AI เพื่อประกอบการสังเกตการณ์เท่านั้น ไม่สามารถใช้แทนเอกสารรับรองทางวิศวกรรมหรือผลการตรวจสอบอย่างเป็นทางการตามกฎหมายได้<br>
        2. หากภาพถ่ายมีความคลาดเคลื่อน มีแสงสว่างไม่เพียงพอ หรือมีความละเอียดต่ำ อาจส่งผลกระทบต่อความแม่นยำในการวิเคราะห์ <strong>หากท่านพบว่ารายงานไม่สอดคล้องกับหน้างานจริง กรุณาอัปโหลดภาพถ่ายใหม่ที่คมชัดในมุมที่หลากหลายขึ้น</strong><br>
        3. เพื่อความปลอดภัยสูงสุด โปรดปรึกษาวิศวกรควบคุมงานหรือผู้เชี่ยวชาญหน้างานเพื่อยืนยันความถูกต้องตามมาตรฐานวิชาชีพก่อนการดำเนินงานในขั้นตอนถัดไป
    </div>
    """, unsafe_allow_html=True)
