import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)

# 2. ตรวจสอบ API Key
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("❌ ไม่พบ API Key ในระบบ")
    st.stop()

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

# --- ส่วนใหม่: เมนูเลือกบุคลิก AI ---
st.markdown("### 🛠️ เลือกรูปแบบการวิเคราะห์ที่ท่านต้องการ")
analysis_mode = st.radio(
    "ระบบของ BHOON KHARN พร้อมช่วยคุณในรูปแบบดังนี้:",
    ["⚡ สรุปประเด็นด่วน (Quick Scan)", 
     "🛠️ คู่มือตรวจงานเอง (Self-Check Guide)", 
     "📖 คัมภีร์สำหรับมือใหม่ (Beginner's Handbook)"],
    index=1
)

# 4. ส่วนอัพโหลดรูป
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. แบบแปลน (ถ้ามี)")
    blue_file = st.file_uploader("เลือกไฟล์แบบ", type=['jpg', 'png', 'jpeg'], key="blue")
    if blue_file: st.image(blue_file, use_container_width=True)

with col2:
    st.subheader("2. รูปหน้างานจริง")
    site_file = st.file_uploader("เลือกรูปหน้างาน", type=['jpg', 'png', 'jpeg'], key="site")
    if site_file: st.image(site_file, use_container_width=True)

# 5. ปุ่มเริ่มงาน
if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
    if blue_file or site_file:
        with st.spinner('ระบบ BHOON KHARN AI กำลังวิเคราะห์ข้อมูล...'):
            try:
                # ปรับบุคลิกและเนื้อหาตามโหมด
                if "สรุปประเด็นด่วน" in analysis_mode:
                    mode_prompt = """
                    สำเนียง: เป็นวิศวกรที่พูดน้อย ต่อยหนัก เน้นความเร็ว
                    เนื้อหา: สรุปเฉพาะจุดที่ 'เสี่ยง' หรือ 'ผิดปกติ' เป็นข้อสั้นๆ 
                    ใช้สัญลักษณ์ [🚨 วิกฤต] สำหรับจุดที่ต้องหยุดงานทันที และ [⚠️ ควรเช็ค] สำหรับจุดที่ต้องสังเกต
                    """
                elif "คู่มือตรวจงานเอง" in analysis_mode:
                    mode_prompt = """
                    สำเนียง: เป็นพี่เลี้ยงช่างที่ใจดีและมีความรู้ลึก
                    เนื้อหา: บอกจุดที่น่าสังเกต พร้อม 'วิธีการตรวจเช็คด้วยตัวเอง' (เช่น การวัด, การใช้สายตา) 
                    และให้คำถามที่ควรไปถามช่างเพื่อให้ดูเป็นมืออาชีพ 
                    เน้นย้ำเรื่องเทคนิค: ห้ามเติมน้ำในคอนกรีต, ระยะเวลาบ่มปูนก่อนทาสี, การเลือกสีรองพื้น
                    """
                else: # คัมภีร์สำหรับมือใหม่
                    mode_prompt = """
                    สำเนียง: เป็นเพื่อนคู่คิดที่เข้าใจความกังวลของเจ้าของบ้าน
                    เนื้อหา: อธิบายภาพรวมว่าที่เห็นในรูปคืออะไร มีความสำคัญยังไง และช่างกำลังจะทำอะไรต่อในวันพรุ่งนี้ 
                    เน้นการปลอบโยนและสร้างความมั่นใจ โดยอธิบายศัพท์ช่างให้เป็นภาษาบ้านๆ
                    """

                common_instruction = f"""
                จากการวิเคราะห์ของ AI ของ BHOON KHARN:
                {mode_prompt}
                
                หากพบจุดวิกฤตที่ส่งผลต่อโครงสร้างหรือความปลอดภัย ให้มาร์คจุดนั้นด้วยสีแดงหรือแจ้งว่า [สำคัญมาก]
                ท้ายรายงานให้สรุป 'สิ่งที่ต้องห้ามทำ' ในขั้นตอนถัดไปให้ชัดเจน
                """
                
                content_to_send = [common_instruction]
                if blue_file: content_to_send.append(Image.open(blue_file))
                if site_file: content_to_send.append(Image.open(site_file))

                response = model.generate_content(content_to_send)
                
                st.divider()
                st.subheader(f"📋 ผลการวิเคราะห์: {analysis_mode}")
                st.markdown(response.text)
                
                st.error("""
                **🚨 หมายเหตุ:** ข้อมูลนี้เป็นเพียงข้อสังเกตจาก AI เพื่อช่วยสังเกตการณ์งานก่อสร้างเท่านั้น 
                โปรดตรวจสอบความถูกต้องหน้างานร่วมกับวิศวกรหรือผู้ควบคุมงานของท่านอีกครั้งก่อนดำเนินการ
                """)
                
            except Exception as e:
                st.error(f"การประมวลผลล้มเหลว: {e}")
    else:
        st.warning("กรุณาอัพโหลดรูปอย่างน้อย 1 รูปเพื่อให้ AI เริ่มวิเคราะห์ครับ")
