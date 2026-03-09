import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บให้ดูเป็นทางการ (BHOON KHARN Branding)
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ระบบวิเคราะห์หน้างานและผลกระทบต่อเนื่องทางวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบสลับ API Key (Key Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()
genai.configure(api_key=random.choice(all_keys))

# 3. กำหนดโมเดล (ใช้รุ่นที่เสถียรที่สุดเพื่อแก้ปัญหา NotFound)
MODEL_NAME = "gemini-1.5-flash" 
model = genai.GenerativeModel(MODEL_NAME)

# --- ระบบ Session สำหรับเก็บประวัติ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_report" not in st.session_state:
    st.session_state.full_report = ""

# 4. เมนูเลือกรูปแบบการวิเคราะห์
with st.sidebar:
    st.title("⚙️ การตั้งค่า")
    analysis_mode = st.radio(
        "โหมดการวิเคราะห์:",
        ["📊 วิเคราะห์เทคนิคและลำดับงาน (Technical & Linked Works)", 
         "🏠 คู่มือเจ้าของบ้าน (Simplified Checklist)"]
    )
    if st.button("🗑️ ล้างประวัติการคุย"):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.rerun()

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลนก่อสร้าง (เพื่ออ้างอิง)", type=['jpg', 'png', 'jpeg'])
    if blue_file: st.image(blue_file, caption="แบบแปลน", use_container_width=True)
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_file: st.image(site_file, caption="หน้างานปัจจุบัน", use_container_width=True)

# 6. ประมวลผล
if st.button("🚀 วิเคราะห์หน้างาน", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังวิเคราะห์ผลกระทบลูกโซ่...'):
            try:
                # Prompt ใหม่: ปลดล็อกพลัง AI เต็มที่ + ภาษาเจ้าของบ้าน + ผลกระทบงานถัดไป
                prompt = f"""
                คุณคือ 'BHOON KHARN AI Analysis' ผู้เชี่ยวชาญเทคนิคก่อสร้าง 
                วิเคราะห์ภาพนี้โดยแบ่งเนื้อหาดังนี้:
                
                1. 🔍 สิ่งที่เห็น: งานในภาพคืออะไร (สั้น/คม)
                2. ⚠️ ผลกระทบลูกโซ่ (Domino Effect): ถ้าพลาดตรงนี้ งานส่วนไหนจะเสียหายตาม? ค่าซ่อมจะแพงแค่ไหน? 
                3. 🏗️ ข้อมูลเทคนิคเชิงลึก: มาตรฐานวิศวกรรม (วสท./มยผ.) และเทคนิคช่างที่ถูกต้อง (เช่น ระยะห่าง, การกันร้าว, การบ่มปูน)
                4. 🏠 สำหรับเจ้าของบ้าน: วิธีเช็คเองง่ายๆ 1-2-3 (ใช้ภาษาชาวบ้าน เปรียบเทียบภาพชัดเจน)
                5. 💬 คำถามชวนคุย: แนะนำ 3 คำถามที่เจ้าของบ้านควรพิมพ์ถามต่อเพื่อรู้ลึกขึ้น
                
                กฎ: สรุปเป็น Bullet points ให้อ่านง่าย, ไม่ฟันธงเด็ดขาดใช้คำว่า 'น่าสังเกตว่า', โหมดคือ: {analysis_mode}
                """
                
                imgs = []
                if blue_file: imgs.append(Image.open(blue_file))
                if site_file: imgs.append(Image.open(site_file))

                response = model.generate_content([prompt] + imgs)
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = f"--- รายงาน BHOON KHARN AI ---\n\n{response.text}"
                
            except google_exceptions.NotFound:
                st.error("❌ ไม่พบโมเดลที่เรียกใช้ โปรดตรวจสอบว่า API Key ของท่านเปิดใช้งาน Gemini 1.5 Flash แล้ว")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผลรายงานและระบบแชท
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์")
    
    # แสดงรายงานล่าสุด
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ปุ่มดาวน์โหลดรายงานเก็บไว้ดูภายหลัง
    st.download_button(
        label="📥 ดาวน์โหลดสรุปรายงานเก็บไว้ (Text)",
        data=st.session_state.full_report,
        file_name="BHOON_KHARN_Analysis.txt",
        mime="text/plain"
    )

    # ช่องแชทถามต่อเชิงลึก
    st.info("💡 สงสัยจุดไหน? พิมพ์ถามด้านล่างเพื่อขอข้อมูลเชิงลึกเพิ่มได้ทันทีครับ")
    if prompt_chat := st.chat_input("พิมพ์คำถามของท่านที่นี่..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})

        with st.chat_message("assistant"):
            with st.spinner("กำลังหาข้อมูลเทคนิคเพิ่มเติม..."):
                chat_response = model.generate_content(f"ในฐานะ BHOON KHARN AI วิเคราะห์เชิงลึกจากคำถามนี้: {prompt_chat}")
                st.markdown(chat_response.text)
                st.session_state.full_report += f"\n\nคำถาม: {prompt_chat}\nคำตอบ: {chat_response.text}"
        st.session_state.messages.append({"role": "assistant", "content": chat_response.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์นี้เป็นเพียงการสังเกตการณ์เบื้องต้น โปรดปรึกษาวิศวกรของท่านเพื่อความถูกต้องทางกฎหมาย")
