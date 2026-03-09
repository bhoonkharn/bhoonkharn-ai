import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN AI
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบดึง API Key จาก Secrets
def get_all_api_keys():
    try:
        keys = []
        if "GOOGLE_API_KEY" in st.secrets:
            keys.append(st.secrets["GOOGLE_API_KEY"])
        for key in st.secrets.keys():
            if "GOOGLE_API_KEY" in key and st.secrets[key] not in keys:
                keys.append(st.secrets[key])
        return keys
    except:
        return []

all_keys = get_all_api_keys()

# 3. ฟังก์ชันโหลดโมเดลอัจฉริยะ (แก้ปัญหา 404 โดยการหา Model ที่ใช้ได้จริง)
@st.cache_resource
def initialize_bhoonkharn_ai(keys):
    if not keys:
        return None, "ไม่พบกุญแจในระบบ (Secrets ว่างเปล่า)"
    
    random_keys = keys.copy()
    random.shuffle(random_keys)
    
    last_error = ""
    for key in random_keys:
        try:
            genai.configure(api_key=key)
            
            # --- จุดสำคัญ: ค้นหาโมเดลที่กุญแจนี้รองรับจริง ---
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if not available_models:
                continue

            # เลือกตัวที่เก่งที่สุด (ลำดับ: Flash > Pro > อื่นๆ)
            target = ""
            # ค้นหารุ่น Flash ก่อนเพราะเร็วและประหยัด
            flash_gen = [m for m in available_models if "flash" in m.lower()]
            if flash_gen:
                target = flash_gen[0]
            else:
                target = available_models[0] # ถ้าไม่มี Flash เอาตัวแรกที่ส่งงานได้

            model = genai.GenerativeModel(target)
            # ทดสอบเรียกสั้นๆ
            model.generate_content("test") 
            return model, f"Success ({target})"
        except Exception as e:
            last_error = str(e)
            continue
            
    return None, f"กุญแจใช้ไม่ได้: {last_error}"

# ตรวจสอบการเชื่อมต่อ
if "active_model" not in st.session_state or st.session_state.active_model is None:
    model, status = initialize_bhoonkharn_ai(all_keys)
    st.session_state.active_model = model
    st.session_state.conn_status = status

model = st.session_state.active_model

# ระบบ Session สำหรับเก็บประวัติ
if "messages" not in st.session_state: st.session_state.messages = []
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "suggested_questions" not in st.session_state: st.session_state.suggested_questions = []

# 4. เครื่องมือทางด้านซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if model:
        st.success(f"🟢 {st.session_state.conn_status}")
    else:
        st.error(f"🔴 {st.session_state.get('conn_status', 'ไม่สามารถเชื่อมต่อได้')}")
        if st.button("🔄 ลองเชื่อมต่อใหม่"):
            st.session_state.active_model = None
            st.rerun()
            
    st.divider()
    analysis_mode = st.radio(
        "รูปแบบรายงาน:",
        ["📊 วิเคราะห์ทางเทคนิคเชิงลึก", "🏠 สรุปประเด็นเจ้าของบ้าน"]
    )
    
    if st.button("🗑️ ล้างประวัติงานนี้", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.session_state.suggested_questions = []
        st.rerun()

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุอ้างอิง", type=['jpg', 'png', 'jpeg'])
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริงที่ต้องการตรวจ", type=['jpg', 'png', 'jpeg'])

def ask_bhoonkharn(query):
    if not model:
        st.error("AI ไม่พร้อมใช้งาน")
        return
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"): st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์..."):
            res = model.generate_content(f"ตอบคำถามเชิงลึกในฐานะ BHOON KHARN: {query}")
            st.markdown(res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {res.text}"
            st.session_state.messages.append({"role": "assistant", "content": res.text})

# 6. ปุ่มเริ่มวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not model:
        st.error("กรุณาตรวจสอบการเชื่อมต่อ API")
    elif site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                # Prompt แบบเน้นวิเคราะห์ความเสี่ยงและห้ามแนะนำตัว
                prompt = f"""
                ห้ามแนะนำตัว ห้ามทักทาย ให้เริ่มรายงานทันทีดังนี้:
                🔍 [วิเคราะห์หน้างาน]: ระบุหมวดงานและสถานะปัจจุบัน
                ⚠️ [ผลกระทบต่อเนื่อง]: Domino Effect และผลเสียต่องบประมาณ
                🏗️ [มาตรฐานเทคนิค]: มาตรฐานเชิงลึกและปัจจัยเรื่องเวลา/อายุวัสดุ
                🏠 [มุมเจ้าของบ้าน]: วิธีตรวจเช็คเอง 1-2-3 (ภาษาง่ายๆ เปรียบเทียบชัดเจน)
                💬 [คำถามชวนคุยต่อ]: แนะนำ 3 คำถามสำคัญที่ขึ้นต้นด้วย 'ถามช่าง:'
                รูปแบบ: {analysis_mode}
                """
                imgs = [Image.open(f) for f in [blue_file, site_file] if f]
                response = model.generate_content([prompt] + imgs)
                
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
                questions = re.findall(r"ถามช่าง: (.+)", response.text)
                st.session_state.suggested_questions = [q.strip() for q in questions[:3]]
                st.rerun()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูปครับ")

# 7. แสดงรายงานและปุ่ม Quick Reply
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการตรวจสอบโดย BHOON KHARN AI")
    st.download_button("📥 ดาวน์โหลดรายงานสรุป", data=st.session_state.full_report, file_name="BHOON_KHARN_Report.txt")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if st.session_state.suggested_questions:
        st.info("💡 **คลิกเพื่อสอบถามรายละเอียดเพิ่มได้ทันที:**")
        for q in st.session_state.suggested_questions:
            if st.button(f"🔎 {q}", key=f"q_{hash(q)}", use_container_width=True):
                ask_bhoonkharn(q)
                st.rerun()

    if prompt_chat := st.chat_input("พิมพ์คำถามถามต่อเนื่องจากรายงานนี้..."):
        ask_bhoonkharn(prompt_chat)

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์เบื้องต้นโดย BHOON KHARN AI โปรดตรวจสอบร่วมกับวิศวกรผู้ควบคุมงานเพื่อความถูกต้อง")
