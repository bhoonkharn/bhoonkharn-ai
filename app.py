import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: เน้นความคลีน สัดส่วนถูกต้อง และสีแดงเลือดหมู
st.markdown("""
    <style>
    /* ข้อกำหนดการใช้งาน: สีแดงเลือดหมู */
    .disclaimer-text {
        color: #8B0000 !important;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    /* จุดสังเกตเจ้าของบ้าน: คลีนๆ ไม่จ้าตา */
    .homeowner-box {
        padding: 5px 0 5px 20px;
        border-left: 4px solid #1E3A8A;
        margin-bottom: 20px;
        color: #31333F;
        line-height: 1.7;
    }
    /* ปรับปุ่มถามต่อให้เล็กและสะอาดตาที่สุด */
    div.stButton > button {
        font-size: 0.7rem !important;
        height: 26px !important;
        padding: 0px 10px !important;
        color: #666 !important;
        border-radius: 4px !important;
    }
    /* หัวข้อถามต่อ: เล็กและถ่อมตัว */
    .q-label {
        font-size: 0.7rem;
        color: #999;
        margin-bottom: 8px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
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
def init_bhoonkharn_ai(keys):
    if not keys: return None, "ไม่พบ API Key"
    random.shuffle(keys)
    for k in keys:
        try:
            genai.configure(api_key=k)
            model = genai.GenerativeModel("gemini-1.5-flash")
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    engine, status = init_bhoonkharn_ai(get_working_keys())
    st.session_state.engine = engine
    st.session_state.status = status

# ระบบ Session เก็บข้อมูล
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar แถบตั้งค่าด้านซ้าย
with st.sidebar:
    st.header("⚙️ BHOON KHARN AI")
    if st.session_state.engine: st.success("🟢 ระบบพร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status')}")
    
    if st.button("🔄 รีเซ็ตระบบ"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ (ล็อกตำแหน่งไว้ด้านบน)
col_l, col_r = st.columns(2)
with col_l:
    blueprint = st.file_uploader("📋 แบบแปลน / สเปกวัสดุ", type=['jpg', 'png', 'jpeg'])
    if blueprint: st.image(blueprint, caption="แบบอ้างอิง", use_container_width=True)
with col_r:
    site_photo = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_photo: st.image(site_photo, caption="หน้างานจริง", use_container_width=True)

# ฟังก์ชันส่งคำถามต่อเนื่อง
def run_query(q):
    if not st.session_state.engine: return
    st.session_state.chat_history.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN AI: " + q)
    st.session_state.chat_history.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน")
    elif site_photo or blueprint:
        with st.spinner('BHOON KHARN AI กำลังวิเคราะห์...'):
            try:
                # Prompt: สั่งห้ามใช้ HTML และให้ใช้ Markdown Bullet (*) เท่านั้น
                prompt = (
                    "คุณคือที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพก่อสร้างโดยเริ่มทันที:\n"
                    "🔍 วิเคราะห์หน้างาน: (ระบุงานและสถานะปัจจุบัน)\n"
                    "⏱️ จุดตายวิกฤต: (ระบุความเสี่ยงที่ต้องระวัง)\n"
                    "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect และงบประมาณซ่อม)\n"
                    "🏗️ มาตรฐานเทคนิค: (วสท./มยผ./สากล)\n"
                    "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (สรุปเป็นข้อๆ โดยใช้เครื่องหมาย * นำหน้า ห้ามใช้รหัส HTML ห้ามใช้ <br/>)\n"
                    "ท้ายรายงานแนะนำ 3 คำถามสั้นๆ ขึ้นต้นด้วย 'ถามช่าง:'"
                )
                
                inputs = [prompt]
                if blueprint: inputs.append(Image.open(blueprint))
                if site_photo: inputs.append(Image.open(site_photo))
                
                resp = st.session_state.engine.generate_content(inputs)
                full_txt = resp.text
                
                # แยกคำถามด่วน
                qs = re.findall(r"ถามช่าง: (.+)", full_txt)
                st.session_state.quick_qs = [q.strip() for q in qs[:3]]
                
                # ทำความสะอาดรายงาน
                report_only = re.sub(r"ถามช่าง: .*", "", full_txt, flags=re.DOTALL).strip()
                st.session_state.final_report = report_only
                st.session_state.chat_history = [{"role": "assistant", "content": report_only}]
                st.rerun()
            except Exception as e:
                st.error("เกิดข้อผิดพลาด: " + str(e))
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# --- 6. ส่วนการแสดงผล (ล็อกตำแหน่ง Container ไว้ด้านบนเพื่อกันหน้าจอเด้ง) ---
report_placeholder = st.container()

if st.session_state.final_report:
    with report_placeholder:
        st.divider()
        st.subheader("📋 ผลการตรวจสอบโดย BHOON KHARN AI")
        
        raw_text = st.session_state.final_report
        headers = [
            ("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"),
            ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
            ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"),
            ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
            ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")
        ]
        
        # ระบบแยกหัวข้อแบบ Position-based (เสถียรที่สุด)
        pos = []
        for title, pat in headers:
            m = re.search(pat, raw_text)
            if m: pos.append((m.start(), title, m.end()))
        pos.sort()
        
        if not pos:
            st.markdown(raw_text)
        else:
            for i in range(len(pos)):
                s_content = pos[i][2]
                e_content = pos[i+1][0] if i+1 < len(pos) else len(raw_text)
                title = pos[i][1]
                content = raw_text[s_content:e_content].strip().strip(':').strip()
                
                if "🔍" in title:
                    st.info(content)
                elif "🏠" in title:
                    # ส่วนเจ้าของบ้าน: คลีนๆ ไม่จ้าตา
                    st.markdown(f"#### {title}")
                    st.markdown("<div class='homeowner-box'>", unsafe_allow_html=True)
                    st.markdown(content)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    with st.expander(f"**{title}**"):
                        st.markdown(content)

        st.download_button("📥 บันทึกรายงาน", st.session_state.final_report, "BK_Report.txt")

        # ส่วนถามต่อ (Small UI)
        if st.session_state.quick_qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            btn_cols = st.columns(len(st.session_state.quick_qs))
            for idx, q_txt in enumerate(st.session_state.quick_qs):
                if btn_cols[idx].button(f"🔎 {q_txt}", key=f"bkbtn_{idx}", use_container_width=True):
                    run_query(q_txt)

    # ประวัติการคุยต่อ (จะเลื่อนลงมาต่อท้ายรายงาน)
    if len(st.session_state.chat_history) > 1:
        st.divider()
        for msg in st.session_state.chat_history[1:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_input := st.chat_input("สอบถามเพิ่มเติม..."):
        run_query(user_input)

    # 7. ข้อกำหนดการใช้งาน (Maroon)
    st.markdown("""
    <div class="disclaimer-text">
        <strong>ข้อกำหนดการใช้งาน:</strong><br>
        • การวิเคราะห์นี้เป็นการประเมินเบื้องต้นจากข้อมูลรูปถ่ายเท่านั้น ข้อมูลที่ได้รับอาจไม่ครบถ้วนและไม่สามารถใช้แทนการตรวจสอบหน้างานจริงโดยวิศวกรวิชาชีพได้<br>
        • ความแม่นยำขึ้นอยู่กับความคมชัดของภาพที่ท่านอัปโหลด หากรูปภาพไม่ชัดเจนแนะนำให้ถ่ายภาพใหม่ในมุมที่หลากหลายขึ้น<br>
        • โปรดปรึกษาวิศวกรควบคุมงานของท่านก่อนดำเนินการใดๆ เพื่อความปลอดภัยสูงสุด
    </div>
    """, unsafe_allow_html=True)
