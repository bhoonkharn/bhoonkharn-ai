import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บและ Branding
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและผลกระทบต่อเนื่องเชิงลึก</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบ API Key (Key Rotation)
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ Secrets")
    st.stop()

# 3. ระบบโหลดโมเดล (Robust & White Label)
@st.cache_resource
def load_bhoonkharn_model(api_key):
    genai.configure(api_key=api_key)
    try:
        # ดึงรายชื่อรุ่นที่ใช้ได้และเลือกตัวที่ดีที่สุด
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in available_models if 'flash' in m.lower()]
        target_model = flash_models[0] if flash_models else available_models[0]
        return genai.GenerativeModel(target_model)
    except:
        return None

# สุ่มกุญแจและโหลดโมเดลเบื้องหลัง
model = load_bhoonkharn_model(random.choice(all_keys))
if not model:
    st.stop()

# --- ระบบ Session สำหรับเก็บประวัติ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_report" not in st.session_state:
    st.session_state.full_report = ""

# 4. 🛠️ ดึงเครื่องมือกลับมาที่แถบเมนูทางซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    st.write("สถานะระบบ: 🟢 พร้อมวิเคราะห์")
    st.divider()
    
    analysis_mode = st.radio(
        "เลือกรูปแบบข้อมูล:",
        ["📊 วิเคราะห์เทคนิคและลำดับงาน (Technical Insight)", 
         "🏠 คู่มือสำหรับเจ้าของบ้าน (Simplified Guide)"]
    )
    
    st.divider()
    if st.button("🗑️ ล้างประวัติและเริ่มใหม่", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.rerun()

# 5. ส่วนอัปโหลดรูป (หน้าหลัก)
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลน / สเปกวัสดุอ้างอิง", type=['jpg', 'png', 'jpeg'])
    if blue_file: st.image(blue_file, caption="แบบอ้างอิง", use_container_width=True)
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริงที่ต้องการตรวจ", type=['jpg', 'png', 'jpeg'])
    if site_file: st.image(site_file, caption="หน้างานปัจจุบัน", use_container_width=True)

# 6. ประมวลผล (Universal Intelligence Logic)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังวิเคราะห์ปัจจัยวิกฤต...'):
            try:
                # Prompt ที่สอนวิธีคิดแบบวิศวกร (ไม่เจาะจงงาน)
                universal_prompt = f"""
                คุณคือ 'BHOON KHARN AI Analysis' ที่ปรึกษาเทคนิคอัจฉริยะ
                วิเคราะห์ภาพนี้โดยใช้กระบวนการคิดดังนี้:

                1. 🔍 [ระบุหน้างาน]: วิเคราะห์ทันทีว่าคือหมวดงานอะไร (ไฟฟ้า, ประปา, โครงสร้าง, ฯลฯ)
                2. ⏱️ [ปัจจัยวิกฤตที่มองไม่เห็น]: ตรวจสอบ 'เวลา' และ 'อายุวัสดุ' (เช่น อายุคอนกรีต, วันหมดอายุ) หรือจังหวะเวลาที่ควรจะเป็น
                3. ⚠️ [ผลกระทบลูกโซ่ (Domino Effect)]: หากจุดนี้พลาด งานถัดไปส่วนไหนจะเสียหาย? ค่าซ่อมจะบานปลายแค่ไหน?
                4. 🏗️ [มาตรฐานวิศวกรรม]: ดึงความรู้เชิงลึก (วสท./มยผ./สากล) มาอธิบายมาตรฐานที่ถูกต้อง
                5. 🏠 [มุมเจ้าของบ้าน]: แปลเป็นภาษาง่ายๆ 1-2-3 พร้อมวิธีตรวจเช็คเอง
                6. 💬 [คำถามชวนคุยต่อ]: แนะนำคำถามสำคัญที่สุดให้เจ้าของบ้านไปถามผู้รับเหมาต่อ
                
                กฎ: ใช้สัญลักษณ์ Emoji, แบ่งหัวข้อชัดเจน, สุภาพและมืออาชีพ, ไม่แทนตัวว่าเป็นอาจารย์
                โหมดการตอบ: {analysis_mode}
                """
                
                imgs = []
                if blue_file: imgs.append(Image.open(blue_file))
                if site_file: imgs.append(Image.open(site_file))

                response = model.generate_content([universal_prompt] + imgs)
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
            except Exception as e:
                st.error(f"ระบบไม่สามารถเข้าถึงโมเดลได้ชั่วคราว: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผลรายงานและระบบแชท
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์โดย BHOON KHARN AI")
    
    st.download_button(
        label="📥 ดาวน์โหลดรายงานสรุป (Text)",
        data=st.session_state.full_report,
        file_name="BHOON_KHARN_Analysis.txt",
        mime="text/plain"
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ช่องแชทถามตอบต่อเนื่อง
    if prompt_chat := st.chat_input("มีข้อสงสัยเพิ่มเติม? พิมพ์ถาม BHOON KHARN AI ได้เลย..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})

        with st.chat_message("assistant"):
            with st.spinner("กำลังค้นหาข้อมูลเทคนิค..."):
                chat_res = model.generate_content(f"ในฐานะ BHOON KHARN AI วิเคราะห์เชิงลึกจากคำถามนี้: {prompt_chat}")
                st.markdown(chat_res.text)
                st.session_state.full_report += f"\n\nคำถาม: {prompt_chat}\nคำตอบ: {chat_res.text}"
        st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์เบื้องต้นโดย BHOON KHARN AI โปรดปรึกษาวิศวกร
