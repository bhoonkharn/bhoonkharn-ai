import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงเชิงวิศวกรรม</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการ API Key
def get_working_keys():
    keys = []
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "GOOGLE_API_KEY" in k and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_bhoonkharn_engine(keys):
    if not keys: return None, "ไม่พบ API Key"
    shuffled_keys = keys.copy()
    random.shuffle(shuffled_keys)
    for k in shuffled_keys:
        try:
            genai.configure(api_key=k)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0] if models else None
            if not target: continue
            model = genai.GenerativeModel(target)
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

# ตรวจสอบสถานะการเชื่อมต่อ
if "active_engine" not in st.session_state:
    engine, status = init_bhoonkharn_engine(get_working_keys())
    st.session_state.active_engine = engine
    st.session_state.status_msg = status

engine = st.session_state.active_engine

# ระบบ Session ข้อมูล
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. แถบเครื่องมือด้านซ้าย (Sidebar)
with st.sidebar:
    st.title("⚙️ การตั้งค่าระบบ")
    if engine: st.success("🟢 BHOON KHARN AI: พร้อมใช้งาน")
    else: st.error(f"🔴 สถานะ: {st.session_state.get('status_msg', 'ขัดข้อง')}")
    
    if st.button("🔄 รีเซ็ตการเชื่อมต่อ"):
        st.session_state.active_engine = None
        st.rerun()
    st.divider()
    mode = st.radio("โหมดรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดและพรีวิวรูปภาพ
col_left, col_right = st.columns(2)
with col_left:
    blueprint = st.file_uploader("📋 อัปโหลดแบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
    if blueprint: st.image(blueprint, caption="แบบอ้างอิง", use_container_width=True)
with col_right:
    site_photo = st.file_uploader("📸 อัปโหลดภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_photo: st.image(site_photo, caption="หน้างานจริง", use_container_width=True)

# ฟังก์ชันส่งคำถามต่อเนื่อง
def run_query(q):
    if not engine: return
    st.session_state.chat_history.append({"role": "user", "content": q})
    with st.chat_message("user"): st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์..."):
            res = engine.generate_content(f"วิเคราะห์เชิงลึกในฐานะ BHOON KHARN AI: {q}")
            st.markdown(res.text)
            st.session_state.final_report += f"\n\nถาม: {q}\nตอบ: {res.text}"
            st.session_state.chat_history.append({"role": "assistant", "content": res.text})

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not engine: st.error("ระบบ AI ไม่พร้อมใช้งาน กรุณาตรวจสอบ API Key")
    elif site_photo or blueprint:
        with st.spinner('BHOON KHARN AI กำลังประมวลผลข้อมูลทางวิศวกรรม...'):
            try:
                prompt = f"""
                ห้ามแนะนำตัว ห้ามทักทาย ให้เริ่มรายงานทันทีที่หัวข้อแรก:
                🔍 [วิเคราะห์หน้างาน]: ระบุงานและสถานะปัจจุบัน
                ⏱️ [จุดตายที่ต้องระวัง]: วิเคราะห์เรื่องเวลา อายุวัสดุ และความเสี่ยงแฝง
                ⚠️ [ผลกระทบต่อเนื่อง]: Domino Effect หากพลาดจุดนี้จะกระทบงานไหนและงบเท่าไหร่
                🏗️ [มาตรฐานเทคนิค]: มาตรฐาน วสท./สากล ที่ต้องใช้เช็ค
                🏠 [วิธีเช็คเอง 1-2-3]: ขั้นตอนตรวจสอบง่ายๆ สำหรับเจ้าของบ้าน
                💬 [คำถามถามต่อ]: แนะนำ 3 คำถามสั้นๆ (ไม่เกิน 15 คำ) เริ่มด้วย 'ถามช่าง:'
                รูปแบบ: {mode}, ใช้ Emoji, เน้นตัวหนาจุดวิกฤต
                """
                imgs = [Image.open(f) for f in [blueprint, site_photo] if f]
                resp = engine.generate_content([prompt] + imgs)
                st.session_state.chat_history = [{"role": "assistant", "content": resp.text}]
                st.session_state.final_report = resp.text
                # ดึงคำถามมาทำปุ่ม
                found_qs = re.findall(r"ถามช่าง: (.+)", resp.text)
                st.session_state.quick_qs = [q.strip() for q in found_qs[:3]]
                st.rerun()
            except Exception as e: st.error(f"เกิดข้อผิดพลาด: {e}")
    else: st.warning("กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูปครับ")

# 6. แสดงผลลัพธ์และระบบถามตอบ
if st.session_state.final_report:
    st.divider()
    st.markdown("### 📋 รายงานสรุปโดย BHOON KHARN AI")
    st.download_button("📥 ดาวน์โหลดรายงาน (.txt)", st.session_state.final_report, "BK_Analysis.txt")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # ปุ่มคำถามด่วน (Quick Reply)
    if st.session_state.quick_qs:
        st.write("---")
        st.info("💡 **คำถามแนะนำ (คลิกเพื่อถามต่อ):**")
        for q_text in st.session_state.quick_qs:
            if st.button(f"🔎 {q_text}", key=f"btn_{hash(q_text)}", use_container_width=True):
                run_query(q_text)
                st.rerun()

    if user_q := st.chat_input("พิมพ์คำถามเพิ่มเติมที่นี่..."):
        run_query(user_q)

    st.caption("🚨 หมายเหตุ: รายงานเบื้องต้นเพื่อการสังเกตการณ์ โปรดปรึกษาวิศวกรหน้างานเพื่อความถูกต้อง 100%")
