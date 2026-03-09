import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="BHOON KHARN AI", layout="centered")
st.markdown("<h1 style='text-align: center; color: #333;'>🏗️ BHOON KHARN AI Inspector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ระบบช่วยสังเกตการณ์และเตรียมความพร้อมงานก่อสร้าง</p>", unsafe_allow_html=True)

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
        with st.spinner('ระบบกำลังประมวลผลข้อมูลเชิงช่าง...'):
            try:
                content_to_send = []
                
                # ปรับ Prompt ให้เน้นการตรวจสอบก่อนงานถัดไปและใส่ความรู้เฉพาะทาง
                common_instruction = """
                จากการวิเคราะห์ของ AI ของ BHOON KHARN:
                ให้คุณสวมบทบาทเป็นที่ปรึกษาเจ้าของบ้านที่เน้น 'การป้องกันปัญหาล่วงหน้า'
                
                โครงสร้างการตอบต้องประกอบด้วย:
                1. 🔍 สิ่งที่น่าสังเกตในปัจจุบัน: (วิเคราะห์จากรูปว่าตอนนี้ทำถึงขั้นไหน และมีอะไรน่าสนใจ)
                2. 🚩 จุดที่ต้องตรวจสอบ 'ทันที' (สำคัญมาก): หากมีจุดเสี่ยงให้แจ้งเป็นข้อความที่เน้นความสำคัญ 
                3. 🚧 เตรียมตัวสำหรับงานขั้นถัดไป (Pre-check): แนะนำสิ่งที่เจ้าของบ้านต้องดูให้ดีก่อนช่างจะเริ่มงานต่อไป เช่น:
                   - หากเป็นงานแบบหล่อคอนกรีต: ต้องเตือนเรื่องการตรวจสอบความแข็งแรงแบบหล่อ และย้ำว่า 'ห้ามช่างเติมน้ำในคอนกรีต' เพื่อไม่ให้ค่ากำลังอัดเสีย
                   - หากเป็นงานก่อฉาบ: ต้องแนะนำเรื่องการรอกี่วันถึงทาสี (ปกติ 14-21 วัน) และควรใช้สีรองพื้นปูนใหม่กันด่างก่อนทาสีจริง
                4. 💡 วิธีการคุยกับช่าง: แนะนำคำถามที่เจ้าของบ้านควรใช้ถามช่างในขั้นตอนนี้

                หมายเหตุ: หากเป็นจุดที่วิกฤตหรืออันตราย ให้ใช้เครื่องหมาย 🚨 หรือแจ้งว่า [สำคัญมาก]
                """
                
                if blue_file and site_file:
                    prompt = common_instruction + "\nเปรียบเทียบแบบและหน้างาน เพื่อดูความพร้อมก่อนเริ่มงานขั้นต่อไป"
                    content_to_send = [prompt, Image.open(blue_file), Image.open(site_file)]
                elif site_file:
                    prompt = common_instruction + "\nวิเคราะห์หน้างานจริงและเตรียม Checklist สำหรับสิ่งที่จะเกิดขึ้นในวันถัดไป"
                    content_to_send = [prompt, Image.open(site_file)]
                else:
                    prompt = common_instruction + "\nวิเคราะห์จุดสำคัญในแบบที่เจ้าของบ้านต้องกำชับช่างก่อนเริ่มทำจริง"
                    content_to_send = [prompt, Image.open(blue_file)]

                response = model.generate_content(content_to_send)
                
                st.divider()
                st.subheader("📋 รายงานและข้อแนะนำจาก BHOON KHARN AI")
                
                # ใช้ Markdown แสดงผลเพื่อให้ AI สามารถเน้นตัวหนาหรือสีได้
                st.markdown(response.text)
                
                # Disclaimer ด้านกฎหมาย (เพิ่มความเข้มข้น)
                st.error("""
                **🚨 คำเตือนด้านความปลอดภัย:** ข้อมูลนี้เป็นการประมวลผลด้วย AI เบื้องต้นเพื่อเป็นคู่มือสังเกตการณ์เท่านั้น 
                ห้ามใช้แทนการตัดสินใจของวิศวกรวิชาชีพในกรณีที่เกี่ยวข้องกับโครงสร้างและความปลอดภัย 
                ควรปรึกษาผู้ควบคุมงานของท่านก่อนดำเนินการในขั้นตอนสำคัญเสมอ
                """)
                
            except Exception as e:
                st.error(f"การประมวลผลล้มเหลว: {e}")
    else:
        st.warning("กรุณาอัพโหลดรูปเพื่อให้ AI ช่วยตรวจสอบครับ")
