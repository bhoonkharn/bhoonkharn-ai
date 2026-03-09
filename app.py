import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random
import re

# 1. ตั้งค่าหน้าเว็บและ Branding (BHOON KHARN AI)
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบดึง API Key จาก Secrets (รองรับหลายกุญแจ)
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

# 3. ฟังก์ชันโหลดโมเดลอัจฉริยะ (White Label - ซ่อนชื่อรุ่น AI)
@st.cache_resource
def initialize_bhoonkharn_ai(keys):
    if not keys:
        return None, "ไม่พบกุญแจในระบบ"
    
    random_keys = keys.copy()
    random.shuffle(random_keys)
    
    last_error = ""
    for key in random_keys:
        try:
            genai.configure(api_key=key)
            # ค้นหาโมเดลที่ใช้ได้จริงเบื้องหลัง
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            flash_gen = [m for m in available_models if "flash" in m.lower()]
            target = flash_gen[0] if flash_gen else available_models[0]
            
            model = genai.GenerativeModel(target)
            model.generate_content("test") # ทดสอบการเชื่อมต่อ
            return model, "พร้อมวิเคราะห์"
        except Exception as e:
            last_error = str(e)
            continue
            
    return None, f"เชื่อมต่อล้มเหลว: {last_error}"

# จัดการ Session สำหรับ Model และข้อมูลแชท
if "active_model" not in st.session_state or st.session_state.active_model is None:
    model, status = initialize_bhoonkharn_ai(all_keys)
    st.session_state.active_model = model
    st.session_state.conn_status = status

model = st.session_state.active_model

if "messages" not in st.session_state: st.session_state.messages = []
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "suggested_questions" not in st.session_state: st.session_state.suggested_questions = []

# 4. แถบเครื่องมือทางด้านซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if model:
        st.success("🟢 สถานะระบบ: พร้อมใช้งาน")
    else:
        st.error(f"🔴 สถานะ: {st.session_state.get('conn_status', 'ขัดข้อง')}")
        if st.button("🔄 พยายามเชื่อมต่อใหม่"):
            st.session_state.active_model = None
            st.rerun()
            
    st.divider()
    analysis_mode = st.radio(
        "รูปแบบการนำเสนอ:",
        ["📊 วิเคราะห์เทคนิคและผลกระทบต่อเนื่อง", "🏠 คู่มือสำหรับเจ้าของบ้าน (เข้าใจง่าย)"]
    )
    
    if st.button("🗑️ ล้างประวัติการตรวจสอบ", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.session_state.suggested_questions = []
        st.rerun()

# 5. ส่วนอัปโหลดรูป (หน้าหลัก)
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุอ้างอิง", type=['jpg', 'png', 'jpeg'])
    if blue_file: st.image(blue_file, caption="เอกสารอ้างอิง", use_container_width=True)
with col2:
    site_file = st.file_uploader("ภาพถ่ายหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_file: st.image(site_file, caption="หน้างานปัจจุบัน", use_container_width=True)

# ฟังก์ชันสำหรับส่งคำถาม (ทั้งพิมพ์เองและปุ่มกด)
def ask_bhoonkharn(query):
    if not model:
        st.error("AI ไม่พร้อมใช้งาน")
        return
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"): 
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("BHOON KHARN AI กำลังวิเคราะห์เชิงลึก..."):
            res = model.generate_content(f"ในฐานะที่ปรึกษา BHOON KHARN ตอบคำถามเชิงลึก: {query}")
            st.markdown(res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {res.text}"
            st.session_state.messages.append({"role": "assistant", "content": res.text})

# 6. เริ่มการวิเคราะห์หลัก (Universal Intelligence Logic)
if st.button("🚀 เริ่มการวิเคราะห์หน้างาน", use_container_width=True):
    if not model:
        st.error("กรุณาเชื่อมต่อ API ก่อนเริ่มงาน")
    elif site_file or blue_file:
        with st.spinner('กำลังประมวลผลตามมาตรฐาน BHOON KHARN...'):
            try:
                # ปรับ Prompt ให้คมชัด ไม่ทักทาย และเน้น Risk-Based
                prompt = f"""
                จงสวมบทบาทนักตรวจสอบหน้างานมืออาชีพจาก BHOON KHARN
                ห้ามแนะนำตัว ห้ามทักทาย ห้ามทวนคำสั่ง ให้เริ่มรายงานทันทีดังนี้:

                🔍 [วิเคราะห์หน้างาน]: ระบุหมวดงานและสถานะปัจจุบัน (กระชับ/คม)
                ⏱️ [ปัจจัยวิกฤตที่มองไม่เห็น]: ตรวจสอบ 'เวลา' 'อายุวัสดุ' หรือจังหวะการทำงานที่อาจเป็นจุดตาย
                ⚠️ [ผลกระทบต่อเนื่อง (Domino Effect)]: หากจุดนี้พลาด งานถัดไปจะเสียหายอย่างไร และกระทบงบประมาณแค่ไหน
                🏗️ [มาตรฐานเทคนิคเชิงลึก]: ดึงมาตรฐานวิศวกรรม (วสท./มยผ./สากล) มาอธิบายเชิงลึก
                🏠 [มุมเจ้าของบ้าน]: วิธีตรวจเช็คเอง 1-2-3 (ภาษาง่ายๆ เปรียบเทียบภาพชัดเจน)
                💬 [คำถามชวนคุยต่อ]: แนะนำ 3 คำถามสำคัญที่ขึ้นต้นด้วย 'ถามช่าง:' เพื่อให้เจ้าของบ้านไปถามต่อ
                
                รูปแบบ: ใช้ Emoji นำหัวข้อ, ตัวหนาประเด็นสำคัญ, สรุปเป็น Bullet points
                โหมด: {analysis_mode}
                """
                
                imgs = [Image.open(f) for f in [blue_file, site_file] if f]
                response = model.generate_content([prompt] + imgs)
                
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
                # ดึงคำถามมาทำปุ่ม (Quick Reply)
                questions = re.findall(r"ถามช่าง: (.+)", response.text)
                st.session_state.suggested_questions = [q.strip() for q in questions[:3]]
                st.rerun()
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนเริ่มวิเคราะห์")

# 7. แสดงรายงานและระบบปุ่มกดถามต่อ
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์โดย BHOON KHARN AI")
    
    st.download_button("📥 ดาวน์โหลดรายงานสรุป", data=st.session_state.full_report, file_name="BHOON_K
