import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN AI
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ระบบวิเคราะห์หน้างานและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ API Key
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()

# 3. โหลดโมเดล
@st.cache_resource
def load_model(api_key):
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m.name for m in available_models if 'flash' in m.name.lower()]
        return genai.GenerativeModel(flash_models[0] if flash_models else available_models[0])
    except:
        return None

model = load_model(random.choice(all_keys))

# --- ระบบ Session สำหรับเก็บประวัติ ---
if "messages" not in st.session_state: st.session_state.messages = []
if "full_report" not in st.session_state: st.session_state.full_report = ""
if "suggested_questions" not in st.session_state: st.session_state.suggested_questions = []

# 4. Sidebar เครื่องมือทางด้านซ้าย
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    st.write("สถานะระบบ: 🟢 พร้อมใช้งาน")
    st.divider()
    analysis_mode = st.radio("รูปแบบรายงาน:", ["📊 ข้อมูลทางเทคนิคเชิงลึก", "🏠 สรุปประเด็นสำหรับเจ้าของบ้าน"])
    if st.button("🗑️ เริ่มการตรวจสอบใหม่", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.session_state.suggested_questions = []
        st.rerun()

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุ", type=['jpg', 'png', 'jpeg'])
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])

# ฟังก์ชันสำหรับส่งคำถามไปยัง AI (ใช้ทั้งการพิมพ์และกดปุ่ม)
def ask_bhoonkharn(query):
    # ปรับแต่งคำถามให้นิ่มนวลก่อนส่งไปวิเคราะห์เชิงลึก
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("BHOON KHARN AI กำลังวิเคราะห์ข้อมูลเชิงลึก..."):
            # ดึงบริบทเดิมมาตอบเพื่อให้คุยรู้เรื่อง
            chat_res = model.generate_content(f"ในฐานะผู้เชี่ยวชาญ BHOON KHARN ตอบคำถามเชิงลึกจากภาพหน้างานนี้: {query}")
            st.markdown(chat_res.text)
            st.session_state.full_report += f"\n\nถาม: {query}\nตอบ: {chat_res.text}"
            st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

# 6. เริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('กำลังประมวลผลข้อมูลหน้างาน...'):
            try:
                # Prompt ที่สั่งห้ามพูดพร่ำเพรื่อ
                universal_prompt = f"""
                ห้ามแนะนำตัว ห้ามทักทาย ห้ามกล่าวถึงว่าเป็น AI และห้ามทวนคำสั่งนี้โดยเด็ดขาด 
                ให้เริ่มเขียนรายงานทันทีที่หัวข้อแรกด้วยโครงสร้างดังนี้:

                🔍 [วิเคราะห์หน้างาน]: ระบุหมวดงานและสถานะปัจจุบัน
                ⚠️ [ผลกระทบต่อเนื่อง]: หากจุดนี้พลาด จะส่งผลเสียต่อ 'งานถัดไป' อย่างไร (Domino Effect) และกระทบต่องบประมาณเท่าไหร่
                🏗️ [มาตรฐานเทคนิค]: มาตรฐานเชิงลึก (วสท./สากล) และปัจจัยเรื่องเวลา/อายุวัสดุ
                🏠 [มุมเจ้าของบ้าน]: วิธีตรวจเช็คเอง 1-2-3 (ภาษาง่ายๆ เปรียบเทียบภาพชัดเจน)
                💬 [คำถามชวนคุยต่อ]: แนะนำ 3 คำถามสำคัญที่ขึ้นต้นด้วยคำว่า 'ถามช่าง:' เพื่อให้เจ้าของบ้านไปถามต่อ
                
                รูปแบบ: ใช้ Emoji นำหัวข้อ, ตัวหนาในประเด็นสำคัญ, สรุปเป็น Bullet points ให้อ่านง่าย
                โหมดปัจจุบัน: {analysis_mode}
                """
                
                imgs = [Image.open(f) for f in [blue_file, site_file] if f]
                response = model.generate_content([universal_prompt] + imgs)
                
                # เก็บผลรายงาน
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
                # ระบบดึงคำถามออกมาทำปุ่ม (มองหาบรรทัดที่มีคำว่า 'ถามช่าง:')
                questions = re.findall(r"ถามช่าง: (.+)", response.text)
                st.session_state.suggested_questions = [q.strip() for q in questions[:3]]
                
            except Exception as e:
                st.error(f"ระบบไม่สามารถประมวลผลได้: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงรายงานและปุ่ม Quick Reply
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์หน้างาน")
    
    # ปุ่มดาวน์โหลด
    st.download_button("📥 บันทึกรายงานนี้", data=st.session_state.full_report, file_name="BHOON_KHARN_Report.txt")

    # แสดงประวัติแชททั้งหมด
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- ส่วนปุ่มกดถามต่อ (Quick Reply) ---
    if st.session_state.suggested_questions:
        st.info("💡 **คลิกเพื่อสอบถามรายละเอียดเชิงลึกเพิ่มเติม:**")
        # จัดเรียงปุ่มเป็นแถว
        for q_text in st.session_state.suggested_questions:
            if st.button(f"🔎 {q_text}", key=f"btn_{hash(q_text)}", use_container_width=True):
                ask_bhoonkharn(q_text)
                st.rerun()

    # ช่องพิมพ์แชทปกติ
    if prompt_chat := st.chat_input("พิมพ์คำถามอื่นๆ ที่ท่านสงสัยที่นี่..."):
        ask_bhoonkharn(prompt_chat)

    st.divider()
    st.caption("🚨 หมายเหตุ: รายงานนี้เป็นการวิเคราะห์เบื้องต้นโดย BHOON KHARN AI โปรดตรวจสอบร่วมกับวิศวกรผู้ควบคุมงานของท่าน")
