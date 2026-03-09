import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. หน้าเว็บ Branding
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)

# 2. ระบบ API Key
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key")
    st.stop()
genai.configure(api_key=random.choice(all_keys))

# 3. โหลดโมเดล (ใช้รุ่นที่รองรับการวิเคราะห์ภาพและใช้เหตุผลเชิงลึก)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- ระบบ Session ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_report" not in st.session_state:
    st.session_state.full_report = ""

# 4. เมนูเลือกโหมด
analysis_mode = st.radio("เลือกรูปแบบการนำเสนอ:", ["📊 วิเคราะห์ทางเทคนิคและผลกระทบต่อเนื่อง", "🏠 คู่มือสำหรับเจ้าของบ้าน"])

# 5. อัปโหลดรูป (รองรับทั้งแบบและหน้างาน)
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุ", type=['jpg', 'png', 'jpeg'])
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])

# 6. ประมวลผล (Universal Intelligence Prompt)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังวิเคราะห์องค์รวมของงานก่อสร้าง...'):
            try:
                # Prompt ที่สอน "วิธีคิด" ไม่ได้สอน "เนื้อหา"
                universal_prompt = f"""
                คุณคือ 'BHOON KHARN AI Analysis' ที่ปรึกษาเทคนิคอัจฉริยะ 
                จงวิเคราะห์ภาพถ่ายงานก่อสร้างหรืองานตกแต่งนี้ โดยใช้กระบวนการคิดดังนี้:

                1. 🔍 [การระบุหน้างาน]: วิเคราะห์ว่าคืองานหมวดใด (ไฟฟ้า, ประปา, โครงสร้าง, ฝ้า, ครัว, ฯลฯ) และอยู่ในสถานะใด
                
                2. ⏱️ [ปัจจัยวิกฤตที่มองไม่เห็น]: ตรวจสอบ 'เวลา' ในภาพ (ถ้ามี) และวิเคราะห์ 'อายุของวัสดุ' 
                   - เช่น อายุคอนกรีต, วันหมดอายุเคมีภัณฑ์, หรือลำดับเวลาที่ควรจะเป็นของงานนั้นๆ
                   - หากภาพไม่มีตัวเลขเวลา ให้ตั้งข้อสังเกตเกี่ยวกับ 'จังหวะการทำงาน' ที่เหมาะสม
                
                3. ⚠️ [ผลกระทบลูกโซ่ (Domino Effect)]: หากจุดนี้พลาด จะส่งผลเสียต่อ 'งานถัดไป' อย่างไร? 
                   - เน้นเรื่องความสวยงามในขั้นตอนจบผิว (Finishing) และค่าใช้จ่ายในการรื้อถอนซ่อมแซม
                
                4. 🏗️ [มาตรฐานวิศวกรรม/สถาปัตยกรรม]: ดึงความรู้เชิงลึกเกี่ยวกับงานนั้นๆ มาอธิบาย 
                   - ระยะที่ถูกต้อง, การติดตั้งตามมาตรฐานแบรนด์, หรือกฎหมายอาคารที่เกี่ยวข้อง
                
                5. 🏠 [มุมเจ้าของบ้าน]: แปลข้อมูลข้างต้นเป็นภาษาง่ายๆ 1-2-3 พร้อมวิธีตรวจเช็คด้วยตัวเอง
                
                6. 💬 [คำถามชวนคุยต่อ]: แนะนำคำถามที่ 'สำคัญที่สุด' เพื่อให้เจ้าของบ้านไปถามผู้รับเหมาต่อ
                
                กฎการตอบ: ใช้สัญลักษณ์ Emoji, แบ่งหัวข้อชัดเจน, สุภาพและมืออาชีพ, ไม่ฟันธง (ใช้ 'น่าสังเกตว่า')
                โหมดการตอบ: {analysis_mode}
                """
                
                imgs = []
                if blue_file: imgs.append(Image.open(blue_file))
                if site_file: imgs.append(Image.open(site_file))

                response = model.generate_content([universal_prompt] + imgs)
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
            except Exception as e:
                st.error(f"ระบบขัดข้อง: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผลและแชท
if st.session_state.full_report:
    st.divider()
    st.download_button("📥 บันทึกรายงาน (Text)", data=st.session_state.full_report, file_name="BHOON_KHARN_Report.txt")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt_chat := st.chat_input("สอบถามรายละเอียดเชิงลึกเพิ่มเติม..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})
        with st.chat_message("assistant"):
            chat_res = model.generate_content(f"คุณคือ BHOON KHARN AI วิเคราะห์เชิงลึกจากคำถามนี้: {prompt_chat}")
            st.markdown(chat_res.text)
        st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์เบื้องต้นโดย BHOON KHARN AI โปรดปรึกษาวิศวกรเพื่อความถูกต้อง")
