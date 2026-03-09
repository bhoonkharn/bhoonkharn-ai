import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")

st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ที่ปรึกษาอัจฉริยะเคียงข้างเจ้าของบ้าน โดย BHOON KHARN</p>", unsafe_allow_html=True)

# 2. ระบบสลับ API Key (Key Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key")
    st.stop()
genai.configure(api_key=random.choice(all_keys))

# 3. เตรียม AI Model
@st.cache_resource
def find_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower(): return m.name
        return "gemini-1.5-flash"
    except: return "gemini-1.5-flash"

model = genai.GenerativeModel(find_available_model())

# --- ระบบเก็บข้อมูลใน Session สำหรับแชท ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# 4. เมนูเลือกรูปแบบการวิเคราะห์
st.markdown("### 🛠️ รูปแบบข้อมูลที่คุณต้องการ")
analysis_mode = st.radio(
    "เลือกตามความต้องการ:",
    ["⚡ วิเคราะห์เชิงลึกและงานที่เกี่ยวพัน (Technical Focus)", 
     "🏠 คู่มือเช็คหน้างานสำหรับเจ้าของบ้าน (Easy Guide)"],
    index=1
)

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน (เพื่ออ้างอิง)", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, use_container_width=True)
with col2:
    site_file = st.file_uploader("รูปหน้างานจริง", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, use_container_width=True)

# 6. Prompt วิชาช่าง (BHOON KHARN Knowledge Base)
# ใส่ข้อมูลที่คุณต้องการให้ AI ทราบและใช้ในการตอบ
bhoonkharn_knowledge = """
วิชาช่างและมาตรฐานจาก BHOON KHARN ที่คุณต้องใช้:
1. งานระบบไฟฟ้า: บล็อกไฟฝังผนังก่อนฉาบ ควรมีระยะห่างจากหน้าอิฐประมาณ 3 ซม. เพื่อให้พอดีกับความหนาปูนฉาบ
2. งานระบบประปาห้องน้ำ: ท่อควรฝังลึกเพียงพอ โดยเผื่อความหนากระเบื้อง (ประมาณ 1 ซม.) และปูนกาว (ประมาณ 0.5 ซม.) ระยะรวมควรให้หน้าวาล์วพอดีกับผิววัสดุ
3. งานผนัง: ระยะเวลาทิ้งให้ปูนฉาบแห้งตัว (Curing) คือ 14-21 วันก่อนทาสี เพื่อป้องกันสีพองหรือด่าง
4. งานคอนกรีต: ห้ามเติมน้ำหน้างานเด็ดขาด เพราะจะทำให้กำลังอัด (Strength) ลดลง
"""

# 7. ปุ่มเริ่มวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                common_instruction = f"""
                คุณคือที่ปรึกษาเทคนิคของ BHOON KHARN (สุภาพ, มืออาชีพ, ไม่แทนตัวว่าเป็นอาจารย์)
                {bhoonkharn_knowledge}
                กฎ: วิเคราะห์ตามรูปจริง, ไม่ฟันธงเด็ดขาดใช้คำว่า 'น่าสังเกตว่า', เน้นการเตรียมตัวสู่งานถัดไป
                """
                
                if "วิเคราะห์เชิงลึก" in analysis_mode:
                    mode_prompt = f"{common_instruction}\nเน้นรายละเอียดเชิงช่างและการเชื่อมโยงงานถัดไป อ้างอิงมาตรฐาน วสท./มยผ."
                else:
                    mode_prompt = f"{common_instruction}\nเน้นวิธีเช็คด้วยตัวเอง 1-2-3 สำหรับเจ้าของบ้านที่ไม่รู้เรื่องช่าง"

                images = []
                if blue_file: images.append(Image.open(blue_file))
                if site_file: images.append(Image.open(site_file))

                response = model.generate_content([mode_prompt] + images)
                
                # เก็บผลลัพธ์ลง Session
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.analysis_done = True
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาอัพโหลดรูปภาพก่อนครับ")

# 8. แสดงผลการวิเคราะห์และระบบแชทถามตอบ
if st.session_state.analysis_done:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์จาก BHOON KHARN AI")
    
    # แสดงประวัติแชท
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ช่องแชทถามต่อ (Chat Input)
    if prompt := st.chat_input("สงสัยจุดไหน สอบถามที่ปรึกษา AI เพิ่มเติมได้เลยครับ..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("กำลังหาคำตอบให้ครับ..."):
                # ส่งรูป + ประวัติแชท + คำถามใหม่ ให้ AI
                chat_context = [f"คุณคือที่ปรึกษา BHOON KHARN ข้อมูลช่าง: {bhoonkharn_knowledge}"]
                if blue_file: chat_context.append(Image.open(blue_file))
                if site_file: chat_context.append(Image.open(site_file))
                chat_context.append(f"คำถามจากลูกค้า: {prompt}")
                
                chat_response = model.generate_content(chat_context)
                st.markdown(chat_response.text)
        st.session_state.messages.append({"role": "assistant", "content": chat_response.text})

    st.divider()
    st.caption("🚨 AI เป็นผู้ช่วยสังเกตการณ์เบื้องต้น โปรดปรึกษาวิศวกรของท่านเพื่อความถูกต้องตามหลักวิศวกรรม")
