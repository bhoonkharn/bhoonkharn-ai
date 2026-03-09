import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random

# 1. ตั้งค่าหน้าเว็บ (BHOON KHARN Branding)
st.set_page_config(page_title="BHOON KHARN AI Analysis", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างเชิงลึกและผลกระทบต่อเนื่องอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบสลับ API Key
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]
if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()

# 3. ระบบโหลดโมเดล (White Label - ซ่อนชื่อรุ่น)
@st.cache_resource
def load_bhoonkharn_model(api_key):
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m.name for m in genai.list_models() if 'flash' in m.name.lower()]
        target_model = flash_models[0] if flash_models else available_models[0]
        return genai.GenerativeModel(target_model)
    except:
        return None

model = load_bhoonkharn_model(random.choice(all_keys))
if not model:
    st.stop()

# --- ระบบ Session สำหรับเก็บประวัติแชท ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_report" not in st.session_state:
    st.session_state.full_report = ""

# 4. เมนู Sidebar
with st.sidebar:
    st.title("⚙️ การจัดการ")
    st.write("สถานะระบบ: 🟢 พร้อมใช้งาน (BHOON KHARN AI)")
    analysis_mode = st.radio(
        "โหมดการวิเคราะห์:",
        ["📊 วิเคราะห์เทคนิคและผลกระทบต่อเนื่อง", "🏠 คู่มือเจ้าของบ้านฉบับย่อยง่าย"]
    )
    if st.button("🗑️ ล้างข้อมูลและเริ่มใหม่"):
        st.session_state.messages = []
        st.session_state.full_report = ""
        st.rerun()

# 5. ส่วนอัปโหลดรูป
col1, col2 = st.columns(2)
with col1:
    blue_file = st.file_uploader("แบบแปลนก่อสร้างอ้างอิง", type=['jpg', 'png', 'jpeg'])
    if blue_file: st.image(blue_file, caption="แบบแปลน", use_container_width=True)
with col2:
    site_file = st.file_uploader("ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_file: st.image(site_file, caption="หน้างานปัจจุบัน", use_container_width=True)

# 6. ประมวลผล (Core Analysis)
if st.button("🚀 เริ่มการวิเคราะห์เชิงลึก", use_container_width=True):
    if site_file or blue_file:
        with st.spinner('BHOON KHARN AI กำลังประมวลผลข้อมูลทางวิศวกรรม...'):
            try:
                # Prompt ที่เน้นสัญลักษณ์และความสวยงาม + คำถามชวนคุยต่อ
                prompt = f"""
                คุณคือ 'BHOON KHARN AI Analysis' ผู้เชี่ยวชาญเทคนิคก่อสร้างอิสระ
                วิเคราะห์ภาพนี้โดยแบ่งเนื้อหาเป็นหัวข้อพร้อมใส่สัญลักษณ์ (Emoji) ดังนี้:
                
                🔍 [สิ่งที่เห็นจากภาพ]: สรุปสั้นๆ ว่างานถึงขั้นตอนไหน
                
                ⚠️ [ผลกระทบลูกโซ่ (Domino Effect)]: สำคัญมาก! ถ้าพลาดตรงนี้ งานไหนจะเสียตาม? ค่าซ่อมจะบานปลายแค่ไหน?
                
                🏗️ [ข้อมูลเทคนิคเชิงลึก]: มาตรฐานวิศวกรรมสากล/วสท./มยผ. (ระยะ, วัสดุ, มาตรฐานช่าง)
                
                🏠 [วิธีเช็คด้วยตัวเอง]: ขั้นตอน 1-2-3 สำหรับเจ้าของบ้าน (ภาษาง่ายๆ เปรียบเทียบชัดเจน)
                
                💬 [คำถามที่ท่านอาจสงสัย]: แนะนำ 3 คำถามที่เจ้าของบ้านควรพิมพ์ถามต่อเพื่อรู้ลึกขึ้นในงานส่วนนี้
                
                กฎ: 
                - ใช้ Bullet points และ Bold ข้อความสำคัญเพื่อให้อ่านง่าย
                - ห้ามฟันธงเด็ดขาด ใช้คำว่า 'น่าสังเกตว่า' 
                - ห้ามแทนตัวว่าเป็นอาจารย์ ให้ใช้บุคลิกที่ปรึกษาเทคนิค BHOON KHARN
                - โหมดปัจจุบัน: {analysis_mode}
                """
                
                imgs = []
                if blue_file: imgs.append(Image.open(blue_file))
                if site_file: imgs.append(Image.open(site_file))

                response = model.generate_content([prompt] + imgs)
                st.session_state.messages = [{"role": "assistant", "content": response.text}]
                st.session_state.full_report = response.text
                
            except Exception as e:
                st.error(f"ระบบขัดข้องชวนคราว: {e}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# 7. แสดงผลรายงานและระบบแชทต่อเนื่อง
if st.session_state.full_report:
    st.divider()
    st.markdown("### 📋 ผลการวิเคราะห์จาก BHOON KHARN AI")
    
    # ปุ่มดาวน์โหลด
    st.download_button(
        label="📥 ดาวน์โหลดสรุปรายงานเก็บไว้ (Text)",
        data=st.session_state.full_report,
        file_name="BHOON_KHARN_Analysis.txt",
        mime="text/plain"
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ส่วนแชทถามตอบต่อเนื่อง
    st.info("💡 **คุยกับ BHOON KHARN AI ต่อได้ที่นี่:** พิมพ์คำถามตามคำแนะนำด้านบน หรือข้อสงสัยอื่นๆ ได้ทันทีครับ")
    if prompt_chat := st.chat_input("พิมพ์คำถามของท่านเพื่อสอบถามรายละเอียดเชิงลึก..."):
        with st.chat_message("user"):
            st.markdown(prompt_chat)
        st.session_state.messages.append({"role": "user", "content": prompt_chat})

        with st.chat_message("assistant"):
            with st.spinner("BHOON KHARN AI กำลังหาข้อมูลเทคนิคเพิ่มเติม..."):
                # ส่งประวัติแชทเบื้องต้นไปให้ AI เพื่อการตอบต่อเนื่อง
                chat_res = model.generate_content(f"ในฐานะ BHOON KHARN AI ตอบคำถามเชิงลึกจากภาพนี้: {prompt_chat}")
                st.markdown(chat_res.text)
                st.session_state.full_report += f"\n\nคำถาม: {prompt_chat}\nคำตอบ: {chat_res.text}"
        st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

    st.divider()
    st.caption("🚨 หมายเหตุ: ผลวิเคราะห์นี้เป็นเพียงการสังเกตการณ์เบื้องต้น โปรดปรึกษาวิศวกรของท่านเพื่อความถูกต้องทางกฎหมาย")
