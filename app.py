import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions as google_exceptions
import random # เพิ่มตัวช่วยสุ่มกุญแจ

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)

# 2. ระบบสุ่มเลือก API Key (Key Rotation)
# ระบบจะดึงกุญแจทุกดอกที่ชื่อมีคำว่า GOOGLE_API_KEY มาเก็บไว้
all_keys = [v for k, v in st.secrets.items() if "GOOGLE_API_KEY" in k]

if not all_keys:
    st.error("❌ ไม่พบ API Key ในระบบ Secrets")
    st.stop()

# สุ่มกุญแจขึ้นมา 1 ดอกในแต่ละครั้งที่ลูกค้าใช้งาน
selected_key = random.choice(all_keys)
genai.configure(api_key=selected_key)

# 3. ระบบค้นหาโมเดลอัตโนมัติ
@st.cache_resource
def find_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower(): return m.name
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models[0] if models else None
    except: return None

selected_model_name = find_available_model()
model = genai.GenerativeModel(selected_model_name) if selected_model_name else None

# --- ส่วนเมนูและการอัพโหลด (เหมือนเดิม) ---
st.markdown("### 🛠️ เลือกรูปแบบการวิเคราะห์ที่ท่านต้องการ")
analysis_mode = st.radio(
    "ระบบของ BHOON KHARN พร้อมช่วยคุณในรูปแบบดังนี้:",
    ["⚡ สรุปประเด็นด่วน (Quick Scan)", 
     "🛠️ คู่มือตรวจงานเอง (Self-Check Guide)", 
     "📖 คัมภีร์สำหรับมือใหม่ (Beginner's Handbook)"],
    index=1
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("1. แบบแปลน (ถ้ามี)")
    blue_file = st.file_uploader("เลือกไฟล์แบบ", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, use_container_width=True)
with col2:
    st.subheader("2. รูปหน้างานจริง")
    site_file = st.file_uploader("เลือกรูปหน้างาน", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, use_container_width=True)

if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบกำลังประมวลผล (กำลังใช้กุญแจสำรอง)...'):
            try:
                # ปรับ Prompt ตามโหมด
                if "สรุปประเด็นด่วน" in analysis_mode:
                    mode_prompt = "สำเนียง: วิศวกรเน้นความเร็ว เนื้อหา: สรุปจุดเสี่ยงสั้นๆ ใช้ [🚨 วิกฤต] และ [⚠️ ควรเช็ค]"
                elif "คู่มือตรวจงานเอง" in analysis_mode:
                    mode_prompt = "สำเนียง: พี่เลี้ยงช่างผู้เชี่ยวชาญ เนื้อหา: สอนวิธีตรวจเช็คด้วยตัวเอง เน้นเรื่องห้ามเติมน้ำในปูนและการบ่มปูน"
                else:
                    mode_prompt = "สำเนียง: เพื่อนคู่คิดมือใหม่ เนื้อหา: อธิบายศัพท์ช่างเป็นภาษาบ้านๆ และบอกขั้นตอนงานถัดไป"

                common_instruction = f"จากการวิเคราะห์ของ AI ของ BHOON KHARN:\n{mode_prompt}\nหากพบจุดวิกฤตให้เน้นตัวหนาหรือ 🚨"
                
                content_to_send = [common_instruction]
                if blue_file: content_to_send.append(Image.open(blue_file))
                if site_file: content_to_send.append(Image.open(site_file))

                response = model.generate_content(content_to_send)
                st.divider()
                st.subheader(f"📋 ผลการวิเคราะห์: {analysis_mode}")
                st.markdown(response.text)
                st.info("💡 ท่านสามารถนำผลวิเคราะห์นี้ไปปรึกษาผู้ควบคุมงานเพื่อความถูกต้องแม่นยำยิ่งขึ้น")

            except google_exceptions.ResourceExhausted:
                st.warning("### ⏳ กุญแจดอกนี้เต็มแล้ว!")
                st.write("ระบบกำลังพยายามสลับไปใช้กุญแจสำรองดอกอื่น...")
                st.info("👉 **รบกวนพี่กดปุ่ม 'เริ่มการวิเคราะห์' อีกครั้งทันทีครับ** ระบบจะสุ่มกุญแจดอกใหม่ให้ครับ")
            except Exception as e:
                st.error(f"ขออภัย ระบบขัดข้องชั่วคราว: {str(e)}")
            
            st.divider()
            st.caption("🚨 หมายเหตุ: ข้อมูลนี้เป็นเพียงข้อสังเกตจาก AI เพื่อช่วยสังเกตการณ์งานก่อสร้างเท่านั้น")
    else:
        st.warning("กรุณาอัพโหลดรูปอย่างน้อย 1 รูปครับ")
